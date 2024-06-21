import os
import math
import encodings
from flask import Flask, render_template, request, redirect, url_for
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import language_tool_python
import pandas as pd
import numpy as np
from flask import Flask
from flask import render_template, request
from rake_nltk import Rake

tool = language_tool_python.LanguageTool('en-US')
rake_nltk_var = Rake()

def calculate_cosine_similarity(corpus):
    vectorizer = TfidfVectorizer()
    trsfm = vectorizer.fit_transform(corpus)
    score = cosine_similarity(trsfm[0], trsfm)[0][1] * 10
    return round(score, 2)

def stemmer(keywords_list):
    ps = PorterStemmer()
    for i in range(len(keywords_list)):
        keywords_list[i] = ps.stem(keywords_list[i])
    return keywords_list

def lemmatize(keywords_list):
    lemmatizer = WordNetLemmatizer()
    for i in range(len(keywords_list)):
        keywords_list[i] = lemmatizer.lemmatize(keywords_list[i])
    return keywords_list

corpus = []
app = Flask(__name__)

@app.route('/')
@app.route('/first')
def first():
    return render_template('first.html')

@app.route('/login')
def login():
    return render_template('login.html')

def home():
    return render_template('home.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/trch_login')
def trch_login():
    return render_template('trch_login.html')

@app.route('/stud_login')
def stud_login():
    return render_template('stud_login.html')

@app.route('/preview', methods=["POST"])
def preview():
    if request.method == 'POST':
        dataset = request.files['datasetfile']
        df = pd.read_csv(dataset, encoding='utf-8')
        df.set_index('Id', inplace=True)
        return render_template("preview.html", df_view=df)

@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/success', methods=['POST','GET'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        if f is None:
            return render_template('erroredirect.html', message='empty_file')
        fname = f.filename
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            return render_template('erroredirect.html', message='image_file')
        answer = f.read().decode('utf-8')
        matches = tool.check(answer)
        keywords_correct_answer_list = None

        rake_nltk_var.extract_keywords_from_text(answer)
        keywords_answer_list = rake_nltk_var.get_ranked_phrases()
        print(keywords_answer_list)
        f.close()

        with open("reference.txt", 'r', encoding='utf-8') as fgt:
            corpus.append(fgt.read())
            correct_answer = corpus[0]
            rake_nltk_var.extract_keywords_from_text(correct_answer)
            keywords_correct_answer_list = rake_nltk_var.get_ranked_phrases()
            print(keywords_correct_answer_list)
            fgt.close()
        
        common_keywords = 0
        keywords_answer_list = stemmer(keywords_answer_list)
        keywords_correct_answer_list = stemmer(keywords_correct_answer_list)
        keywords_answer_list = lemmatize(keywords_answer_list)
        keywords_correct_answer_list = lemmatize(keywords_correct_answer_list)
        keywords_answer_list_set = set(keywords_answer_list)
        keywords_correct_answer_list_set = set(keywords_correct_answer_list)
        
        for ka in keywords_answer_list_set:
            for kca in keywords_correct_answer_list_set:
                if ka == kca:
                    common_keywords += 1
        
        complete_list = keywords_answer_list + keywords_correct_answer_list
        unique_keywords = len(np.unique(complete_list))
        keywords_match_score = (common_keywords / unique_keywords) * 10
        corpus.append(answer)
        cosine_sim_score = calculate_cosine_similarity(corpus)
        score = ((6 / 10) * (cosine_sim_score)) + ((4 / 10) * (keywords_match_score))
        
        if score >= 10:
            score = 10
        corpus.clear()
        
        # if len(matches) > 0:
        #     score = score - len(matches)
        
        if score < 0:
            score = 0
        
        print("Errors\t", len(matches))
        print('Cosine_sim_score:\t', cosine_sim_score)
        print('keyword_match_score:\t', keywords_match_score)
        
        return render_template('success.html', name=fname, answer=answer, score=math.ceil(score), correct_answer=correct_answer, matches=len(matches))  
    
    if request.method=='GET':
            return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)
    
