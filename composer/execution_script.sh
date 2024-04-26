 

cd /home/jupyter

echo Copying Python Script

gsutil cp gs://$PROJECT/scripts/script1.py .

echo Executing  Python Script

/opt/conda/bin/python script1.py
