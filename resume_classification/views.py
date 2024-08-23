from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
import docx
from pdf2docx import Converter
import os
import pandas as pd
from teradataml import *
from django.contrib.auth.models import User


import warnings

warnings.filterwarnings("ignore")

def convertpdftodoc(files):
    for file in files:
        # if (os.path.splitext(file)[1] == 'pdf'):
        file_name = file.name
        # print(file_name)
        file_ext = os.path.splitext(file_name)[1]
        # print(file_ext)
        path = default_storage.save(
            os.path.join(settings.RC_MEDIA_ROOT, file_name), ContentFile(file.read())
        )
        final = os.path.join(default_storage.location, path)
        cv = Converter(final)
        basename = os.path.splitext(final)[0]
        cv.convert(basename + ".docx")
        cv.close()


def extracttextfromdoc(directory1, category):
    file_path1 = []
    category1 = []
    ResID1 = []
    for i in os.listdir(directory1):
        if i.endswith(".docx"):
            os.path.join(directory1, i)
            # print("in loop")
            doc = docx.Document(os.path.join(directory1, i))
            fullText = []
            for para in doc.paragraphs:
                fullText.append(para.text)
            print("full txt: ", "\n".join(fullText))
            file_path1.append("\n".join(fullText))
            # file_path1.append((textract.process(os.path.join(directory1, i))).decode('utf-8'))
            category1.append(category)
            ResID1.append(i)
            # print(file_path1,category1,ResID1)

    return (file_path1, category1, ResID1)


def removeUploadedfiles(directory1):
    # print(directory1)
    for i in os.listdir(directory1):
        myfile = i
        filepath = directory1 + "\\" + myfile
        # print(filepath)
        os.remove(filepath)

    print("All Files Deleted")


def cleandata(data1):
    print("Cleaning Data")
    resume_data = data1
    resume_data = resume_data[resume_data["ResID"].isna() == False]
    resume_data = resume_data[resume_data["category"].isna() == False]
    resume_data = resume_data[resume_data["Resume_str"].isna() == False]
    resume_data["ResID"] = pd.to_numeric(resume_data["ResID"].str.replace(".docx", ""))
    resume_data["Resume_str"] = resume_data["Resume_str"].str.replace("\n", " ")
    resume_data.reset_index(drop=True, inplace=True)

    return resume_data


def connectvantage(resume_data, host, username, password):
    print("Connecting to Vantage")
    eng = create_context(host=host, username=username, password=password)
    #  getpass.getpass(prompt = '\nEnter password: '))
    print("ConnectionSuccessful :%s", eng)
    resume_data.to_sql("resume_data_test", eng, if_exists="append", index=False)
    resume_data_test = DataFrame("resume_data_test")

    return resume_data_test


def connectandloaddatafromcsv(host, username, password):
    print("Connecting to Vantage")
    eng = create_context(host=host, username=username, password=password)
    #  getpass.getpass(prompt = '\nEnter password: '))
    print("ConnectionSuccessful :%s", eng)
    types = OrderedDict(ResID=BIGINT, Resume_str=VARCHAR, category=VARCHAR)
    read_csv(
        filepath="./resume_classification/new_resume_data.csv",
        table_name="raw_data_tb",
        types=types,
        if_exists="replace",
    )

    raw_df = DataFrame("raw_data_tb")

    return raw_df


def datapreprocess(resume_data_test):
    print("Parsing text Data and tokenizing for classification")
    TextParser_out = TextParser(
        data=resume_data_test,
        text_column="Resume_str",
        covert_to_lowercase=True,
        output_by_word=True,
        punctuation="\[.,?\!\]",
        remove_stopwords=True,
        stem_tokens=True,
        accumulate=["ResID", "category"],
    )
    copy_to_sql(
        TextParser_out.result, table_name="text_parser_data", if_exists="replace"
    )
    qry = """CREATE MULTISET TABLE resume_tf_idf AS ( SELECT *
        FROM TD_TFIDF(
        ON text_parser_data AS InputTable
        USING
        DocIdColumn ('ResID')
        TokenColumn ('token')
        TFNormalization ('LOG')
        IDFNormalization ('SMOOTH')
        Regularization ('L2')
        Accumulate('category')
        ) AS dt 
    )
    WITH DATA;"""

    try:
        execute_sql(qry)
    except:
        db_drop_table("resume_tf_idf")
        execute_sql(qry)

    tokenize_df = DataFrame("resume_tf_idf")

    return tokenize_df


def datapreprocess_train(raw_df):
    print("Parsing text Data and tokenizing for model training")
    TextParser_out = TextParser(
        data=raw_df,
        text_column="Resume_str",
        covert_to_lowercase=True,
        output_by_word=True,
        punctuation="\[.,?\!\]",
        remove_stopwords=True,
        stem_tokens=True,
        accumulate=["ResID", "category"],
    )
    copy_to_sql(
        TextParser_out.result, table_name="text_parser_data_train", if_exists="replace"
    )

    qry = """CREATE MULTISET TABLE resume_tf_idf_train AS ( SELECT *
            FROM TD_TFIDF(
            ON text_parser_data_train AS InputTable
            USING
            DocIdColumn ('ResID')
            TokenColumn ('token')
            TFNormalization ('LOG')
            IDFNormalization ('SMOOTH')
            Regularization ('L2')
            Accumulate('category')
            ) AS dt ) WITH DATA PRIMARY INDEX(token);"""

    try:
        execute_sql(qry)
    except:
        db_drop_table("resume_tf_idf_train")
        execute_sql(qry)

    tokenize_df_train = DataFrame("resume_tf_idf_train")

    return tokenize_df_train


def buildmodel(tokenize_df_train):
    print("Creating model for classification")
    qry = """SELECT TOP 1 1	
    FROM TD_NaiveBayesTextClassifierTrainer (	
    ON resume_tf_idf_train AS InputTable	
    OUT PERMANENT  TABLE ModelTable (resume_category_model_tb)	
    USING	
    TokenColumn ('token')	
    ModelType ('Multinomial')	
    DocCategoryColumn ('category')	
    ) AS dt;"""

    try:
        execute_sql(qry)
    except:
        db_drop_table("resume_category_model_tb")
        execute_sql(qry)

    return "Model created successfully"


def classifyresume(tokenize_df):
    print("Loading pre-trained model")
    model_df = DataFrame("resume_category_model_tb")
    print("Predicting Resumes")
    nbt_predict_out = NaiveBayesTextClassifierPredict(
        object=model_df,
        newdata=tokenize_df,
        input_token_column="token",
        doc_id_columns="ResID",
        model_type="Multinomial",
        model_token_column="token",
        model_category_column="category",
        model_prob_column="prob",
        newdata_partition_column="ResID",
        output_prob=True,
        accumulate="category",
    )

    predict_df = nbt_predict_out.result
    max_pred_df = predict_df.select(["ResID", "prob"]).groupby("ResID").max()
    final_predict_df = predict_df.merge(
        right=max_pred_df,
        how="inner",
        on=["ResID", "prob=max_prob"],
        lsuffix="l",
        rsuffix="r",
    )
    final_predict_df = final_predict_df.assign(
        drop_columns=True,
        ResID=final_predict_df.ResID_l,
        prediction=final_predict_df.prediction,
        category=final_predict_df.category,
        prob=final_predict_df.prob,
    )

    print("Display Predictions")
    return final_predict_df


def classifyresume_sql(tokenize_df):
    print("Loading pre-trained model")
    model_df = DataFrame("resume_category_model_tb")
    print("Predicting Resumes using pre-trained model")
    qry = """CREATE MULTISET TABLE resume_category_predict AS (
    SELECT *
        FROM NaiveBayesTextClassifierPredict (
        ON resume_tf_idf AS PredictorValues PARTITION BY ResID
        ON resume_category_model_tb AS Model DIMENSION
        USING
        ModelType ('Multinomial')
        InputTokenColumn ('token')
        DocIDColumns ('ResID')
        OutputProb ('true')
        Accumulate('category')
        ) AS dt
    ) WITH DATA;"""

    try:
        execute_sql(qry)
    except:
        db_drop_table("resume_category_predict")
        execute_sql(qry)

    qry = """CREATE MULTISET TABLE final_predictions AS (
    SELECT ResID, category,prediction, prob
        FROM resume_category_predict 
        Qualify prob = max(prob) over(partition by ResID)
    ) WITH DATA;"""

    try:
        execute_sql(qry)
    except:
        db_drop_table("final_predictions")
        execute_sql(qry)

    final_predict_df = DataFrame("final_predictions")

    print("Display Predictions")
    return final_predict_df


def evaluatemodel(final_predict_df):
    print("Evaluate Model")

    ClassificationEvaluator_obj = ClassificationEvaluator(
        data=final_predict_df,
        observation_column="category",
        prediction_column="prediction",
        num_labels=24,
    )

    return ClassificationEvaluator_obj.output_data


def evaluatemodel_sql(final_predict_df):
    print("Evaluate Model")

    qry = """SELECT * FROM TD_ClassificationEvaluator (
        ON final_predictions AS InputTable
        OUT TABLE OutputTable (additional_metrics)
        USING
        ObservationColumn ('category')
        PredictionColumn ('prediction')
        Labels('ADVOCATE','ACCOUNTANT','AVIATION','PUBLIC-RELATIONS',
        'HR','ARTS','CONSTRUCTION','DIGITAL-MEDIA','TEACHER','FITNESS',
        'BUSINESS-DEVELOPMENT','INFORMATION-TECHNOLOGY','APPAREL','BANKING',
        'FINANCE','BPO','CHEF','HEALTHCARE','SALES','CONSULTANT',
        'AUTOMOBILE','ENGINEERING','AGRICULTURE','DESIGNER')
        
        ) AS dt ;"""

    try:
        execute_sql(qry)
    except:
        db_drop_table("additional_metrics")
        execute_sql(qry)

    eval_df = DataFrame("additional_metrics")
    return eval_df


# Create your views here.
def resume_classification(request):
    print(request.method)
    if request.method == "POST":
        user = request.user
        try:
            user_credential = User.objects.get(user=user)
            username = user_credential.username
            password = user_credential.password
            # Use these credentials as needed
        except User.DoesNotExist:
            # Handle the case where credentials do not exist
            pass

        model_id = request.POST.get("model_id")
        print(model_id)
        msg = ""
        if model_id == "1":
            print("Train")
            host = request.POST.get("host")
            username = request.POST.get("username")
            password = request.POST.get("password")
            print("Connect to Vantage and Upload data for model training")
            raw_df = connectandloaddatafromcsv(host, username, password)
            tokenize_df_train = datapreprocess(raw_df)
            msg = buildmodel(raw_df)
            return render(
                request=request,
                template_name="resume_classification/success_train.html",
                context={"param1": msg},
            )
        elif model_id == "2":
            files = request.FILES.getlist("files")
            category1 = request.POST.get("category")
            host = request.POST.get("host")
            username = request.POST.get("username")
            password = request.POST.get("password")

            convertpdftodoc(files)
            directory1 = os.path.join(settings.RC_MEDIA_ROOT)
            print(os.listdir(directory1))
            print(category1)
            file_path1, category1, ResID1 = extracttextfromdoc(directory1, category1)
            data1 = pd.DataFrame(data=file_path1, columns=["Resume_str"])
            data1["category"] = category1
            data1["ResID"] = ResID1
            # print(data1)
            resume_data = cleandata(data1)
            resume_data_test = connectvantage(resume_data, host, username, password)
            tokenize_df = datapreprocess(resume_data_test)
            # print(tokenize_df)
            # final_predict_df = classifyresume(tokenize_df)
            final_predict_df = classifyresume_sql(tokenize_df)
            print(final_predict_df)
            eval_df = evaluatemodel_sql(final_predict_df)
            print(eval_df)
            df = final_predict_df.to_pandas()
            html_table = df.to_html(index=False)
            eval_df_pd = eval_df.to_pandas()
            html_table_metrics = eval_df_pd.to_html(index=False)
            removeUploadedfiles(directory1)
            return render(
                request=request,
                template_name="resume_classification/success.html",
                context={"param1": html_table, "param2": html_table_metrics},
            )

        else:
            # Handle case where no model is selected
            print("Please click on either Train or Predict")

    else:
        pass

    return render(request, "resume_classification/resume_classification.html")
