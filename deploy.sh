#You need to fill out this :) 
# eb init -i

echo "3\nmelon\nY\n1\nN\nn\n" | eb init -i
eb create melon-app
# eb create -t worker melon-worker
aws codepipeline create-pipeline --cli-input-json file://pipeline.json