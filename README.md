# 🛡️ SMS Spam Detector

A supervised learning project that detects spam SMS messages using TF-IDF vectorization and compares 3 classifiers: Naive Bayes, SVM, and Logistic Regression.

## 📁 Project Structure
```
spam-detector/
├── app.py              # Streamlit web app
├── train_model.py      # Model training logic
├── requirements.txt    # Dependencies
├── spam.csv            # Dataset 
└── README.md
```


## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this folder to a **GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → connect your GitHub repo
4. Set main file as `app.py`
5. **Important:** Upload `spam.csv` to your GitHub repo too
6. Click **Deploy** — done! 🎉

---

## 🧠 How It Works

| Step | What happens |
|------|-------------|
| Input | Raw SMS text |
| Vectorization | TF-IDF converts text to numerical features |
| Training | 3 models trained on 80% of 5,574 messages |
| Evaluation | Tested on 20% held-out data |
| Prediction | Best model predicts Spam / Ham with confidence % |

## 📊 Algorithms Used

- **Naive Bayes** — probabilistic classifier, great for text
- **SVM (Support Vector Machine)** — finds optimal decision boundary
- **Logistic Regression** — linear classifier with probability output

## 📚 Dataset
UCI SMS Spam Collection — 5,574 messages labelled as `spam` or `ham`
