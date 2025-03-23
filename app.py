import streamlit as st
import sqlite3
import os
import uuid

# ✅ **Unique User ID Generate** (Tab close hone per reset hoga)
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]  # Unique short ID

USER_ID = st.session_state.user_id
DB_FILE = "library.db"

# 📌 **Create SQLite Database & Table**
def create_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT,
            author TEXT,
            year TEXT,
            genre TEXT,
            read INTEGER,
            image TEXT
        )
    """)
    conn.commit()
    conn.close()

# 📌 **Load Books from Database (Sirf Pehli Dafa)**
def load_books():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, year, genre, read, image FROM books WHERE user_id = ?", (USER_ID,))
    books = [
        {
            "title": row[0],
            "author": row[1],
            "year": row[2],
            "genre": row[3],
            "read": bool(row[4]),
            "image": row[5]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return books

# ✅ **Sirf Pehli Dafa Books Load Karna (Refresh per hatengi nahi)**
if "books" not in st.session_state:
    st.session_state.books = load_books()

# 📌 **Save Books to Database**
def save_book(book):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO books (user_id, title, author, year, genre, read, image) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (USER_ID, book["title"], book["author"], book["year"], book["genre"], int(book["read"]), book["image"]))
    conn.commit()
    conn.close()

    # ✅ **Session Books ko Update karna (Refresh hone per na hatain)**
    st.session_state.books.append(book)

# 📌 **Delete Book from Database**
def delete_book(title):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE user_id = ? AND title = ?", (USER_ID, title))
    conn.commit()
    conn.close()

    # ✅ **Session Books ko Update karna**
    st.session_state.books = [book for book in st.session_state.books if book["title"] != title]

# 🔄 **Initialize Database**
create_db()

# 🏡 **App Title**
st.set_page_config(page_title="📚 Personal Library Manager", layout="wide")

# 📌 **Dark Mode Toggle**
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode", value=False)

# 🎨 **Custom Dark Mode Styling**
if dark_mode:
    st.markdown(
        """
        <style>
            body, .stApp { background-color: #121212 !important; color: white !important; }
            .stSidebar, .sidebar-content { background-color: #1e1e1e !important; color: white !important; }
            input, textarea, select, option { background-color: #333 !important; color: white !important; }
            label, .stCheckbox div label, .stRadio div label { color: white !important; }
            .stButton > button { background-color: #4CAF50 !important; color: white !important; }
            .stButton > button:hover { background-color: #388E3C !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

# 📌 **Main Heading**
st.markdown("# 📚 Personal Library Manager")

# 📚 **Library Collection in Sidebar**
st.sidebar.markdown("## 📖 Library Collection")

if st.session_state.books:
    for book in st.session_state.books:
        st.sidebar.markdown(f"### {book['title']}")
        st.sidebar.write(f"📖 **Author:** {book['author']}")
        st.sidebar.write(f"📅 **Year:** {book['year']}")
        st.sidebar.write(f"📚 **Genre:** {book['genre']}")
        st.sidebar.write(f"✅ **Read:** {'Yes' if book['read'] else 'No'}")

        if book["image"] and os.path.exists(book["image"]):  
            st.sidebar.image(book["image"], caption=book["title"], width=100)

        st.sidebar.markdown("<hr>", unsafe_allow_html=True)

else:
    st.sidebar.write("No books found. Add books to your collection!")

# 📝 **Add New Book Section**
st.markdown("## ➕ Add a New Book")

col1, col2, col3 = st.columns(3)
title = col1.text_input("Book Title", placeholder="Enter book title")
author = col2.text_input("Author", placeholder="Enter author name")
year = col3.text_input("Year", placeholder="Enter publication year")

col4, col5 = st.columns([3, 1])
genre = col4.text_input("Genre", placeholder="Enter book genre")
read = col5.checkbox("Read")

uploaded_image = st.file_uploader("Upload Book Cover Image", type=["jpg", "png", "jpeg"])

# 📂 **Save Image Locally**
image_path = None
if uploaded_image is not None:
    image_folder = "images"
    os.makedirs(image_folder, exist_ok=True)
    image_path = os.path.join(image_folder, uploaded_image.name)
    with open(image_path, "wb") as f:
        f.write(uploaded_image.getbuffer())

if st.button("➕ Add Book"):
    if title and author and year and genre:
        new_book = {"title": title, "author": author, "year": year, "genre": genre, "read": read, "image": image_path}
        save_book(new_book)  # 📌 Save to database
        st.success(f"✅ **{title}** added to the library!")
        st.rerun()
    else:
        st.warning("⚠️ Please fill in all fields.")

# 🔍 **Search Book Section**
st.markdown("## 🔍 Search Book")
search_query = st.text_input("Enter book title or author", placeholder="Search by title or author")

if st.button("🔎 Search"):
    results = [book for book in st.session_state.books if search_query.lower() in book["title"].lower() or search_query.lower() in book["author"].lower()]
    if results:
        for book in results:
            st.write(f"**{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} {'✅' if book['read'] else '❌'}")
    else:
        st.warning("⚠️ No matching books found.")

# 📊 **View Statistics**
st.markdown("## 📊 Library Statistics")
total_books = len(st.session_state.books)
read_books = sum(1 for book in st.session_state.books if book["read"])
read_percentage = (read_books / total_books * 100) if total_books > 0 else 0

st.write(f"📚 Total Books: **{total_books}**")
st.write(f"✅ Read Books: **{read_books}**")
st.write(f"📈 Read Percentage: **{round(read_percentage, 2)}%**")

# ❌ **Remove Book Section**
st.markdown("## ❌ Remove a Book")
book_to_remove = st.selectbox("Select a book to remove", [""] + [book["title"] for book in st.session_state.books])

if st.button("🗑 Remove Book"):
    if book_to_remove:
        delete_book(book_to_remove)  # 📌 Remove from database
        st.success(f"🗑 **{book_to_remove}** removed from the library.")
        st.rerun()
    else:
        st.warning("⚠️ Please select a book to remove.")
