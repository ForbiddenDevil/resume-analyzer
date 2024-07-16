from typing import Dict, List
from django.conf import settings
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .models import JobApplication, Resume
from .forms import JobApplicationForm, ResumeFormSet
from pypdf import PdfReader
import textract
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# -----------------------
# -- Gen AI ------------
# -----------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    return dot_product / (magnitude1 * magnitude2)


def analyze_resume(resume: str, job_description: str) -> Dict[str, float]:
    prompt = f"""Resume:

    {resume}

    Job Description:

    {job_description}

    Instructions:
    1. Analyze the resume and compare it to the job description.
    2. Provide a matching score between 0 and 1, where 1 is a perfect match and 0 is no match at all.
    3. Always return a score, even if the resume doesn't match the job description at all.
    4. Provide a brief explanation for the score (2-3 sentences maximum).
    5. Format your response as follows:
    Score: [numerical value between 0 and 1]
    Explanation: [Your brief explanation]
    6. Do not add any extra punctuation, formatting, or markup in the response.
    7. Focus on key skills, experience, and qualifications when determining the match.

    Example response format:
    Score: 0.7
    Explanation: The candidate has relevant experience in [specific area] and possesses [X] out of [Y] required skills. However, they lack [specific requirement], which prevents a perfect match."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that analyzes resumes and job descriptions.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    analysis = response.choices[0].message.content

    # Extract the score from the analysis
    score_line = [line for line in analysis.split("\n") if "Score:" in line][0]
    score = float(score_line.split(":")[1].strip())

    analysis = analysis.replace(score_line, "")
    analysis = "\n".join([line for line in analysis.split("\n") if line.strip()])
    return {
        "score": score,
        "analysis": analysis,
    }


def rank_resumes(resumes: List[str], job_description: str) -> List[Dict[str, any]]:
    ranked_resumes = []
    for i, resume in enumerate(resumes):

        result = analyze_resume(resume["txt_content"][0], job_description)
        ranked_resumes.append(
            {
                "resume_id": resume["file_name"],
                "score": result["score"],
                "analysis": result["analysis"],
            }
        )

    # Sort resumes by score in descending order
    ranked_resumes.sort(key=lambda x: x["score"], reverse=True)
    return ranked_resumes


def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


def extract_text_from_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_extension in [".doc", ".docx", ".txt", ".rtf"]:
        return textract.process(file_path).decode("utf-8")
    else:
        return "Unsupported file format"


# -------------------------------------------
# -------------------------------------------
# -------------------------------------------


def upload_resume(request):
    if request.method == "POST":

        files = request.FILES.getlist("files")
        file_contents_list = []

        for f in files:
            file_name = f.name
            print("\n\n", f"file_name: {file_name}", "\n\n")
            path = default_storage.save(
                os.path.join(settings.CM_MEDIA_ROOT, file_name), ContentFile(f.read())
            )

            tmp_file = os.path.join(default_storage.location, path)

            # Extract text from the file
            content = extract_text_from_file(tmp_file)

            file_contents = {}
            file_contents["file_name"] = file_name
            file_contents["txt_content"] = content
            file_contents_list.append(file_contents)

        job_description = request.POST.get("job_description")

        resumes = file_contents_list

        ranked_results = rank_resumes(resumes, job_description)

        # filter based on threshold
        threshold_slider = request.POST.get("threshold_slider")
        print("\n\n", f"threshold_slider: {threshold_slider}", "\n\n")

        selected_resumes = [
            i for i in ranked_results if i["score"] >= float(threshold_slider)
        ]
        rejected_resumes = [
            i for i in ranked_results if i["score"] < float(threshold_slider)
        ]

        print("--" * 25)
        print("\n\n", "Final RESULT", "\n\n")
        for result in ranked_results:
            print(f"Resume {result['resume_id']}:")
            print(f"Score: {result['score']}")
            print(f"Analysis: {result['analysis']}")
            print("-" * 50)
        print("--" * 25)
        return render(
            request=request,
            template_name="candidate_matching/matching_score.html",
            context={"param1": selected_resumes, "param2": rejected_resumes},
        )
    else:
        job_form = JobApplicationForm()
        resume_formset = ResumeFormSet(queryset=Resume.objects.none())

    return render(
        request,
        "candidate_matching/upload_resume.html",
        {"job_form": job_form, "resume_formset": resume_formset},
    )


def success(request):
    return render(request, "success.html")
