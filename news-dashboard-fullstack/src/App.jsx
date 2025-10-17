// src/App.jsx
import React, { useState, useEffect } from "react";
import { fetchNews } from "./api";
import NewsCard from "./components/NewsCard";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

function App() {
  const [query, setQuery] = useState("technology");
  const [articles, setArticles] = useState([]); // ✅ INITIALLY EMPTY ARRAY
  const [category, setCategory] = useState("");
  const [country, setCountry] = useState("us");


const getNews = async () => {
  try {
    const data = await fetchNews(query);
    setArticles(Array.isArray(data) ? data : []);
  } catch (err) {
    console.error("Error fetching news:", err);
    setArticles([]);
  }
};




  useEffect(() => {
    getNews();
    // eslint-disable-next-line
  }, []);

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "auto" }}>
      <h1>📰 News Headlines</h1>

      <div style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="Search topic..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select onChange={(e) => setCategory(e.target.value)} value={category}>
          <option value="">All Categories</option>
          <option value="technology">Technology</option>
          <option value="sports">Sports</option>
          <option value="health">Health</option>
          <option value="business">Business</option>
        </select>
        <select onChange={(e) => setCountry(e.target.value)} value={country}>
          <option value="us">USA</option>
          <option value="in">India</option>
          <option value="gb">UK</option>
        </select>
        <button onClick={getNews}>Search</button>
      </div>

      {/* ✅ PLACE THE SNIPPET HERE */}
      <div>
        {Array.isArray(articles) && articles.length > 0 ? (
          articles.map((article, idx) => <NewsCard key={idx} article={article} />)
        ) : (
          <p>No news found.</p>
        )}
      </div>
    </div>
  );
}


export default App;
