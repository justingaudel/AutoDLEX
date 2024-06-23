from flask import Blueprint, render_template,request,url_for,redirect,session
from db_utils import get_db_connection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import base64
import os
import uuid



db_connection = get_db_connection()
cursor = db_connection.cursor()
#prepare data for SVM models
data_sets = [
(" U13-11-372984", "license_number"),
(" Y05-04-823714", "license_number"),
(" E25-09-678132", "license_number"),
(" I21-06-319827", "license_number"),
(" C30-12-582731", "license_number"),
(" W09-08-419827", "license_number"),
(" V14-03-812739", "license_number"),
(" G28-10-927314", "license_number"),
(" O19-07-543217", "license_number"),
(" Z13-05-798213", "license_number"),
(" A02-09-217834", "license_number"),
(" B17-01-982374", "license_number"),
(" K29-11-723489", "license_number"),
(" R15-08-371928", "license_number"),
(" D04-06-823714", "license_number"),
(" P20-04-912873", "license_number"),
(" H10-02-327984", "license_number"),
(" L23-12-982374", "license_number"),
("Q14-12-528394", "license_number"),
    ("G20-05-817439", "license_number"),
    ("B11-03-638472", "license_number"),
    ("R16-09-297485", "license_number"),
    ("F27-01-782364", "license_number"),
    ("T08-10-193847", "license_number"),
    ("S14-04-826394", "license_number"),
    ("W22-01-947263", "license_number"),
    ("J03-04-672489", "license_number"),
    ("F08-06-189274", "license_number"),
    ("M19-11-827364", "license_number"),
    ("A01-01-123456", "license_number"),
    ("B02-02-234567", "license_number"),
    ("C03-03-345678", "license_number"),
    ("D04-04-456789", "license_number"),
    
    (" 2024/12/31", "expiration_date"),
    (" 2025/01/01", "expiration_date"),
    (" 2023/11/30", "expiration_date"),
    (" 2024/10/15", "expiration_date"),
    (" 2023/12/25", "expiration_date"),
    (" 2025/05/20", "expiration_date"),
    (" 2024/08/10", "expiration_date"),
    (" 2023/09/05", "expiration_date"),
    (" 2024/04/18", "expiration_date"),
    (" 2025/02/28", "expiration_date"),
    (" 2024/07/15", "expiration_date"),
    (" 2023/10/31", "expiration_date"),
    (" 2025/03/21", "expiration_date"),
    (" 2024/09/30", "expiration_date"),
    (" 2023/06/12", "expiration_date"),
    (" 2024/05/06", "expiration_date"),
    (" 2025/08/17", "expiration_date"),
    (" 2024/11/22", "expiration_date"),
    (" 2023/04/03", "expiration_date"),
    (" 2025/06/28", "expiration_date"),
    (" 2024/03/08", "expiration_date"),
    (" 2023/02/14", "expiration_date"),
    (" 2025/04/29", "expiration_date"),
    (" 2024/01/05", "expiration_date"),
    (" 2023/08/23", "expiration_date"),
    (" 2025/07/11", "expiration_date"),
    (" 2024/06/19", "expiration_date"),
    (" 2023/05/25", "expiration_date"),
    (" 2025/10/07", "expiration_date"),
    (" 2024/02/11", "expiration_date"),
    (" 2023/01/17", "expiration_date"),
    (" 2025/09/26", "expiration_date"),
    (" 2024/04/01", "expiration_date"),
    (" 2023/03/15", "expiration_date"),
    (" 2025/01/24", "expiration_date"),
    (" 2024/12/30", "expiration_date"),
    (" 2023/11/14", "expiration"),
    ("2024/02/20", "expiration_date"),
    ("2023/07/03", "expiration_date"),
    ("2023/07/03", "expiration_date"),
("2023/08/15", "expiration_date"),
("2025/01/12", "expiration_date"),
("2024/06/23", "expiration_date"),
("2023/09/30", "expiration_date"),
("2025/11/21", "expiration_date"),
("2024/07/05", "expiration_date"),
("2023/03/27", "expiration_date"),
("2025/02/14", "expiration_date"),
("2024/12/19", "expiration_date"),
("2023/10/11", "expiration_date"),
    ("Elijah Santos", "name"),
    ("Sophia Cruz", "name"),
    ("Lucas Rivera", "name"),
    ("Luna Dela Cruz", "name"),
    ("Liam Gonzales", "name"),
    ("Amara Reyes", "name"),
    ("Noah Garcia", "name"),
    ("Chloe Dela Rosa", "name"),
    ("Ethan Aquino", "name"),
    ("Ava Magsaysay", "name"),
    ("Mason Macapagal", "name"),
    ("Harper Bonifacio", "name"),
    ("Jameson Santos", "name"),
    ("Zoe Magalang", "name"),
    ("Ezra Mercado", "name"),
    ("Ella Cruz", "name"),
    ("Logan Dela Rosa", "name"),
    ("Aria Dela Cruz", "name"),
    ("Carter Reyes", "name"),
    ("Layla Santiago", "name"),
    ("Alexander Cruz", "name"),
    ("Scarlett Santos", "name"),
    ("Oliver Reyes", "name"),
    ("Madison Aquino", "name"),
    ("Sebastian Garcia", "name"),
    ("Avery Santos", "name"),
    ("Liam Santiago", "name"),
    ("Charlotte Cruz", "name"),
    ("Daniel Reyes", "name"),
    ("Mia Dela Rosa", "name"),
    ("Benjamin Aquino", "name"),
    ("Lily Cruz", "name"),
    ("Samuel Magalang", "name"),
    ("Evelyn Garcia", "name"),
    ("Henry Santos", "name"),
    ("Luna Reyes", "name"),
    ("Emma Dela Cruz", "name"),
    ("Jack Santiago", "name"),
    ("Sophia Cruz", "name"),
    ("Jacob Reyes", "name"),
    ("Grace Santos", "name"),
    ("Michael Aquino", "name"),
    ("Nora Magsaysay", "name"),
    ("William Macapagal", "name"),
    ("Oliver Reyes", "name"),
("Madison Aquino", "name"),
("Sebastian Garcia", "name"),
("Avery Santos", "name"),
("Liam Santiago", "name"),
("Charlotte Cruz", "name"),
("Daniel Reyes", "name"),
("Mia Dela Rosa", "name"), 
("1990-z01-15", "birthday"),
("1991-02-28", "birthday"),
("1992-03-17", "birthday"),
("1993-04-24", "birthday"),
("1994-05-12", "birthday"),
("1995-06-30", "birthday"),
("1996-07-18", "birthday"),
("1997-08-25", "birthday"),
("1998-09-19", "birthday"),
("1999-10-21", "birthday"),
("2000-11-11", "birthday"),
("2001-12-05", "birthday"),
("2002-01-20", "birthday"),
("2003-02-14", "birthday"),
("2004-03-26", "birthday"),
("2005-04-13", "birthday"),
("1990-02-11", "birthday"),
("1991-03-24", "birthday"),
("1992-04-10", "birthday"),
("1993-05-22", "birthday"),
("1994-06-15", "birthday"),
]

svm_bp = Blueprint("svm", __name__, template_folder="templates")

@svm_bp.route('/violators', methods=['GET', 'POST'])
def violators():
    if request.method == 'POST':
        session['submitted'] = True

        # Get the latest extracted_id
        cursor.execute("SELECT MAX(extracted_id) FROM extracted_data")
        largest_id = cursor.fetchone()[0]

        if largest_id is None:
            new_id = 1
        else:
            cursor.execute("SELECT tct_number FROM extracted_data WHERE extracted_id = %s", (largest_id,))
            existing_tct_number = cursor.fetchone()[0]
            new_id = int(existing_tct_number.split('-')[1]) + 1

        generated_id = 'TCT-' + str(new_id).zfill(5)
        tct_number = generated_id

        # Retrieve form data
        extracted_text = request.form['extracted_text']

        # Prepare data for SVM model
        texts, labels = zip(*data_sets)
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(texts)

        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.4, random_state=42)

        # Train SVM classifier
        svm_classifier = SVC(kernel='linear')
        svm_classifier.fit(X_train, y_train)

        # Evaluate the model
        y_pred = svm_classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print("Accuracy:", accuracy)

        # Predict for new texts
        new_X = vectorizer.transform([extracted_text])
        predictions = svm_classifier.predict(new_X)
        for text, pred_label in zip([extracted_text], predictions):
            print(f"{text} -> Predicted category: {pred_label}")

        # Get image data from the form
        image = request.form.get('image_data')

        # Generate random filename with date
        random_filename = f"{tct_number}_{str(uuid.uuid4())[:8]}.png"
        image_binary = base64.b64decode(image.split(',')[1])

        # Save the image
        image_path = os.path.join('static/extracted_images', random_filename)
        with open(image_path, 'wb') as f:
            f.write(image_binary)

        image_data = random_filename

        # Insert data into the database
        cursor.execute("INSERT INTO extracted_data (extracted_text, tct_number, image_data) VALUES (%s, %s, %s)", (extracted_text, tct_number, image_data))
        db_connection.commit()

        return redirect(url_for('svm.violators', tct_number=tct_number))

    tct_number = request.args.get('tct_number')
    return render_template('violators-form.html', tct_number=tct_number)