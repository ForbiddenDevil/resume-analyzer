from django.conf import settings
from django.shortcuts import render
from openai import OpenAI
from dotenv import load_dotenv
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas as pd
import json

load_dotenv()

# -----------------------
# -- Gen AI ------------
# -----------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_resume(personal_info, professional_info):
    # Combine personal and professional info into a prompt
    prompt = f"""Generate a professional resume based on the following information:

    Personal Details:
    {json.dumps(personal_info, indent=2)}

    Professional Experience:
    {json.dumps(professional_info, indent=2)}

    * Please format the resume in a clear and organized manner
    * Including sections for Personal Information, Summary, Work Experience, Education, and Skills.
    * Give the response with proper markup to shown in HTML page. Do not include <html> and <body> tag in the response.
    * Remember to add image into top of the resume to make it attractive. Use proper circle CSS and HTML tag and keep name besides of it. Keep image with style width: 150px; height: 150px
    * Do not include any extra info tags or information on top of the response like: ```html"""

    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract and return the generated resume
    # return response.choices[0].message['content'].strip()
    return response.choices[0].message.content.strip()


def generate_resume_from_table(df):
    final_resumes = []
    for i, row in df.iterrows():
        print("\n", "-" * 25)
        print("Generating resume for: ", row["Name"])
        personal_info = json.loads(row[:6].to_json(orient="index"))
        professional_info = json.loads(row[6:].to_json(orient="index"))

        # Generate the resume
        resume = generate_resume(personal_info, professional_info)
        resume = resume.replace("```html", "").replace("```", "")
        print("Generated resume for: ", row["Name"])
        # Print the generated resume
        final_resumes.append(resume)

    return final_resumes


# -----------------------
#  upload data
# -----------------------
def upload_data(request):
    if request.method == "POST":

        files = request.FILES.getlist("files")
        if files:
            print("option 1 called...")
            for f in files:
                file_name = f.name
                print("\n\n", f"file_name: {file_name}", "\n\n")
                path = default_storage.save(
                    os.path.join(settings.RG_MEDIA_ROOT, file_name),
                    ContentFile(f.read()),
                )

                tmp_file = os.path.join(default_storage.location, path)

                # Extract text from the file
                df = pd.read_csv(tmp_file)
                # print(df.head())

                final_resumes = generate_resume_from_table(df=df)

                print("\n\n total resumes: ", len(final_resumes), "\n\n")
                print("resume generated..")
        else:
            # option2
            print("option2 called...")
            data_dict = {
                "Name": request.POST.get("name"),
                "Email": request.POST.get("email"),
                "Phone": request.POST.get("phone"),
                "Address": request.POST.get("address"),
                "Hobbies": request.POST.get("hobbies"),
                "LinkedIn": request.POST.get("linkedin"),
                "ProfilePic": request.POST.get("profilepic"),
                "Skills": request.POST.get("skills"),
                "Experience": request.POST.get("experience"),
                "Past Organizations": request.POST.get("pastOrganizations"),
                "Key Projects": request.POST.get("keyProjects"),
                "Education": request.POST.get("education"),
                "Certificates": request.POST.get("certificates"),
                "Awards": request.POST.get("awards"),
            }
            df = pd.DataFrame(data=data_dict, index=[0])
            final_resumes = generate_resume_from_table(df=df)
            print("resume generated..")

        return render(
            request=request,
            template_name="resume_generation/view_generate_resumes.html",
            context={"param1": final_resumes},
        )
    else:
        pass

    return render(
        request,
        "resume_generation/resume_generation.html",
    )


# Create your views here.
def resume_generation(request):
    return render(request, "resume_generation/resume_generation.html")
