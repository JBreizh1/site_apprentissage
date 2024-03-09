# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 12:42:38 2024

@author: Jean-Baptiste
"""

# app.py
from flask import Flask, render_template, request
#import docker
import sys
import docker

#os.chdir("E:\\Docker\\test_flask")
import os
import random
import string
import shutil

app = Flask(__name__)
docker_client = docker.from_env()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    code = request.form['code']
    
    print(os.getcwd())
    path_depart = os.getcwd()
    # Générer un ID aléatoire de 256 caractères
    id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(150))
    
    # Créer un nouveau dossier avec l'ID généré
    os.mkdir(id)
    
    # Accéder au nouveau dossier
    os.chdir(id)
    
    # Créer un fichier `script.py`
    with open("script.py", "w") as f:
        f.write(code)
    
    # Créer un fichier `requirements.txt`
    with open("requirements.txt", "w") as f:
        f.write("""
    urllib3==1.26.15
    """)
    
    
    # Créer un fichier `Dockerfile`
    with open("Dockerfile", "w") as f:
        f.write("""
    FROM python:latest
    
    WORKDIR /app
    
    COPY requirements.txt .
    RUN pip install --upgrade pip
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY . .
    
    CMD ["python3", "script.py"]
    """)
    
    print(f"Un projet Python a été créé dans le dossier '{id}'.")
    try:
        id_docker = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(150))
        id_docker = id_docker.lower()
        docker_client = docker.from_env()
        image, logs = docker_client.images.build(path=".", tag=f"python-{id_docker}")
        #print(image)
        #print(logs)
        # Stocker l'objet conteneur retourné par run
        container = docker_client.containers.run(image=f"python-{id_docker}", name=f"python-run-{id_docker}")
        print(container)
        
        #binary_string = b'hello worl\ncc la team\n'
        
        # Décoder la chaîne binaire en utilisant UTF-8
        code_a_retourner_au_user = container.decode('utf-8')
        
        print(code_a_retourner_au_user)
        
        # Filtrer les conteneurs par statut
        filters = {"status": ["created", "exited"]}
        
        # Obtenir une liste des IDs des conteneurs
        container_ids = [container.id for container in docker_client.containers.list(all=True, filters=filters)]
        
        # Supprimer les conteneurs
        for container_id in container_ids:
            #client.containers.remove(container_id, force=True)
            for container in docker_client.containers.list(all=True, filters=filters):
                container.remove(force=True)
        
        print("Tous les conteneurs avec le statut 'created' ou 'exited' ont été supprimés.")  
        
        docker_client.images.remove(image=image.id)
    
        # Accéder au nouveau dossier
        os.chdir(path_depart)
        
        dossier_a_supprimer = os.getcwd() + f"\{id}"
        
        shutil.rmtree(dossier_a_supprimer)
        
        print(f"Le dossier '{dossier_a_supprimer}' a été supprimé avec succès.")
    except:
        code_a_retourner_au_user="Vous avez fait une erreur dans le code"
        # Accéder au nouveau dossier
        os.chdir(path_depart)
        
        dossier_a_supprimer = os.getcwd() + f"\{id}"
        
        shutil.rmtree(dossier_a_supprimer)
        
        print(f"Le dossier '{dossier_a_supprimer}' a été supprimé avec succès.")
        
    return render_template('result.html', result=code_a_retourner_au_user)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    #app.run(debug=True)