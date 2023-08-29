#! env/bin/python 

import sys, getopt
import yaml
import json
from string import Template
from helper import get_date, to_duration, to_month_year
import subprocess

def open_template(file):
    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return exc

def open_resume(file):
    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return exc

def render(template_file, resume_file, outname, outfmt="pdf"):
    template_data = open_template(template_file)
    if isinstance(template_data, Exception):
        print("unable to open template file")
        return
    else:
        print("template file loaded")
        
    resume_data = json.load(open(resume_file))

    src = render_opening(template_data)
    # ---------------------------
    src += render_header(template_data, resume_data["bio"])
    src += render_contacts(template_data, resume_data["contacts"])
    src += render_sosial_links(template_data, resume_data["social_links"])
    src += render_education(template_data, resume_data["education"])
    src += render_summary(template_data, resume_data["summary"])
    src += render_qualification(template_data, resume_data["qualification"])
    src += render_career_objective(template_data, resume_data["career_objective"])
    src += render_personal_research(template_data, resume_data["personal_research"])
    src += render_experiences(template_data, resume_data["experience"])
    src += render_personal_showcase(template_data, resume_data["personal_showcase"])
    # ---------------------------
    src += render_closing(template_data)

    outpath = "out/" + outname
    target = open(outpath + ".tex", "wt")
    target.write(src)
    target.close()
    result = subprocess.run(["tectonic", outpath + ".tex", "--outfmt", outfmt], capture_output=True, text=True)
    print(result.stdout)

def render_opening(template):
    return template["opening"]

def render_closing(template):
    return template["closing"]

def render_header(template, data):
    gender = "Prefer not to tell gender"
    match data["gender"]:
        case "male": gender = "He/Him"
        case "female": gender = "She/Her"

    code = template["header"]
    name = data["name"]
    dob = data["birth"]["date"]
    nationality = data["nationality"]
    code_tpl = Template(code)
    return code_tpl.substitute(name=name, gender=gender, dob=dob, nationality=nationality)

def render_contacts(template, data):
    code = template["contacts"]
    email = data["email"]
    phone = data["phone"]
    wa_url = data["messaging"]["whatsapp"]["url"]
    wa_label = data["messaging"]["whatsapp"]["label"]
    telegram_url = data["messaging"]["telegram"]["url"]
    telegram_label = data["messaging"]["telegram"]["label"]
    address_city = data["address"]["city"]
    address_utc = data["address"]["utc_offset"]
    address_country = data["address"]["country"]
    code_tpl = Template(code)
    return code_tpl.substitute(email=email, phone=phone, wa_url=wa_url, wa_label=wa_label, 
                             telegram_url=telegram_url, telegram_label=telegram_label, 
                             address_city=address_city, address_utc=address_utc, address_country=address_country)

def render_sosial_links(template, data):
    code = template["social_links"]
    website = data["website"]
    blog = data["blog"]
    linkedin = data["linkedin"]
    twitter = data["twitter"]
    github = data["github"]
    code_tpl = Template(code)
    return code_tpl.substitute(website_url=website["url"], website_label=website["label"],
                             blog_url=blog["url"], blog_label=blog["label"],
                             linkedin_url=linkedin["url"], linkedin_label=linkedin["label"],
                             twitter_url=twitter["url"], twitter_label=twitter["label"],
                             github_url=github["url"], github_label=github["label"])

def render_education(template, data):
    # TODO: need support for multiple education items
    edu = data[0]
    code = template["educations"]
    level = edu["level"]
    major = edu["major"]
    subject = edu["subject"]
    end = edu["end"]
    institution = edu["institution"]
    code_tpl = Template(code)
    return code_tpl.substitute(level=level, major=major, subject=subject, end=end, institution=institution)

def render_summary(template, data):
    code = template["summary"]
    code_tpl = Template(code)
    return code_tpl.substitute(summary=data)

def render_qualification(template, data):
    code = template["qualification"]
    paragraphs = ""
    for paragraph in data:
        paragraphs += paragraph + "\n\n"
    code_tpl = Template(code)
    return code_tpl.substitute(paragraphs=paragraphs)

def render_career_objective(template, data):
    code = template["career_objective"]
    code_tpl = Template(code)
    return code_tpl.substitute(objective=data[0])

def render_personal_research(template, data):
    code = template["personal_research"]
    code_tpl = Template(code)
    return code_tpl.substitute(research=data[0])

def render_experiences(template, data):
    code = template["experience_title"]
    for exp in data:
        code += render_experience(template, exp)
    return code

def render_experience(template, exp):
    item_str = "\item "
    code = template["experience_item"]
    company = exp["company"]
    company_url = exp["company_url"]
    start = to_month_year(exp["start"])
    end = "present" if exp["end"] == "" else to_month_year(exp["end"])
    duration = to_duration(exp["start"], exp["end"])
    position = ", ".join(exp["positions"])
    reports_to = exp["report_to"]
    teams = ", ".join(exp["team"])
    company_description = exp["company_description"]
    responsibilities = "\n".join([item_str + r for r in exp["responsibilities"]])
    accomplishments = "\n".join([item_str + r for r in exp["accomplishments"]])
    techstack = ", ".join(exp["technologies"])
    standards = "(none)" if len(exp["standards"]) == 0 else ", ".join(["\href{" + s["url"] + "}{" + s["name"] + "}" for s in exp["standards"]])
    achievements = "\\vspace{2.6pt}\n(none specific)"
    if len(exp["achievements"]) == 1:
        achievements = "\\vspace{2.6pt}\n" + exp["achievements"][0]
    elif len(exp["achievements"]) > 1:
        achievements = "\n".join([item_str + r for r in exp["achievements"]])
        achievements = "\\begin{itemize}\n" + achievements + "\n\end{itemize}"
    code_tpl = Template(code)
    return code_tpl.substitute(company_url=company_url, company=company, start=start, end=end,
                            duration=duration, position=position, reports_to=reports_to,
                            teams=teams, company_description=company_description,
                            responsibilities=responsibilities, accomplishments=accomplishments,
                            techstack=techstack, standards=standards, achievements=achievements)

def render_personal_showcase(template, data):
    src = template["personal_showcase"]
    rule_str = '\\rule{1.0\\textwidth}{0.1pt}\n'
    # render labs
    src += render_personal_showcase_labs_begin(template)
    i = 0
    for item in data["labs"]:
        src += render_personal_showcase_item(template, item)
        if i < len(data["labs"]) - 1:
            src += rule_str
        i+= 1
    src += render_personal_showcase_labs_end(template)
    
    # render learnings
    src += render_personal_showcase_learnings_begin(template)
    i = 0
    for item in data["learning"]:
        src += render_personal_showcase_item(template, item)
        if i < len(data["learning"]) - 1:
            src += rule_str
        i+= 1
    src += render_personal_showcase_learnings_end(template)
    
    # render projects
    src += render_personal_showcase_projects_begin(template)
    i = 0
    for item in data["projects"]:
        src += render_personal_showcase_item(template, item)
        if i < len(data["projects"]) - 1:
            src += rule_str
        i+= 1
    src += render_personal_showcase_projects_end(template)
    return src

def render_personal_showcase_labs_begin(template):
    return template["personal_showcase_labs_begin"]

def render_personal_showcase_labs_end(template):
    return template["personal_showcase_labs_end"]

def render_personal_showcase_learnings_begin(template):
    return template["personal_showcase_learning_begin"]

def render_personal_showcase_learnings_end(template):
    return template["personal_showcase_learning_end"]

def render_personal_showcase_projects_begin(template):
    return template["personal_showcase_projects_begin"]

def render_personal_showcase_projects_end(template):
    return template["personal_showcase_projects_end"]

def render_personal_showcase_item(template, data):
    match data["type"]:
        case "NameValues":
            return render_name_values(template["name_values"], data)
        case "NameObjects":
            return render_name_objects(template["name_objects"], data)

def render_name_values(template, data):
    code_tpl = Template(template)
    name = data["name"]
    values_str = ", ".join(data["value"])
    return code_tpl.substitute(name=name, values_str=values_str)

def render_name_objects(template, data):
    code_tpl = Template(template)
    name = data["name"]
    values_str = ""
    for item in data["value"]:
        if item["type"] == "NameValues":
            values_str += render_name_values("\item $name ($values_str)\n", item)
    return code_tpl.substitute(name=name, objects=values_str)

# main program
def main(argv):
    tpldir = "templates/"
    tplfile = "academic.yaml"
    outname = "output-resume"
    resumedata = ""
    opts, args = getopt.getopt(argv, "ht:r:o:", ["template", "resume-data", "outname"])
    for opt, arg in opts:
        if opt == "-h":
            print(sys.argv[0] + " -t <template-name> -r <resume-data> -o <outname>")
            sys.exit()
        elif opt in ("-t", "--template"):
            tplfile = arg
        elif opt in ("-r", "--resume-data"):
            resumedata = arg
        elif opt in ("-o", "--outname"):
            outname = arg
    render(tpldir + tplfile, resumedata, outname)

if __name__ == "__main__":
    main(sys.argv[1:])