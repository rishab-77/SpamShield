import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os

def train_and_save():
    # Load dataset
    df = pd.read_csv("spam.csv", encoding='latin-1')[['v1', 'v2']]
    df.columns = ['label', 'message']
    df['label_num'] = df['label'].map({'ham': 0, 'spam': 1})

    X = df['message']
    y = df['label_num']

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Vectorize
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train 3 classifiers
    classifiers = {
        "Naive Bayes": MultinomialNB(),
        "SVM": SVC(kernel='linear', probability=True),
        "Logistic Regression": LogisticRegression(max_iter=1000)
    }

    results = {}
    best_acc = 0
    best_model = None
    best_name = ""

    for name, clf in classifiers.items():
        clf.fit(X_train_vec, y_train)
        y_pred = clf.predict(X_test_vec)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            "accuracy": round(acc * 100, 2),
            "precision": round(report['1']['precision'] * 100, 2),
            "recall": round(report['1']['recall'] * 100, 2),
            "f1": round(report['1']['f1-score'] * 100, 2),
            "confusion_matrix": cm
        }

        if acc > best_acc:
            best_acc = acc
            best_model = clf
            best_name = name

    # Save best model + vectorizer
    with open("model.pkl", "wb") as f:
        pickle.dump(best_model, f)
    with open("vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("results.pkl", "wb") as f:
        pickle.dump({"results": results, "best": best_name}, f)

    print(f"✅ Training complete! Best model: {best_name} ({best_acc*100:.2f}%)")
    return results, best_name

if __name__ == "__main__":
    train_and_save()
