echo "Updating..."
conda activate billy
parallel python3 update.py ::: {1..10}
python3 feedbackupdate.py
python3 text_classify.py