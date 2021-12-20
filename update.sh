echo "Updating..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate billy
parallel python3 /home/user/Documents/小傑/smart-gym-crawler/update.py ::: {1..10}
python3 /home/user/Documents/小傑/smart-gym-crawler/feedbackupdate.py
python3 /home/user/Documents/小傑/smart-gym-crawler/text_classify.py