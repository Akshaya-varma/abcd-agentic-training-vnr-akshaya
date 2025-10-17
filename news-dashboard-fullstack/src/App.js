// src/App.js
import React, { useState, useEffect } from "react";
import { fetchNews } from "./api";
import NewsCard from "./components/NewsCard";
import "./App.css";

function App() {
  const [query, setQuery] = useState("technology");
  const [articles, setArticles] = useState([]);
  const [category, setCategory] = useState("");
  const [country, setCountry] = useState("us");

  const getNews = async () => {
    try {
      const data = await fetchNews(query, category, country);
      setArticles(data);
    } catch (err) {
      console.error("Error fetching news:", err);
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

      <div>
        {articles.length > 0 ? (
          articles.map((article, idx) => <NewsCard key={idx} article={article} />)
        ) : (
          <p>No news found.</p>
        )}
      </div>
    </div>
  );
}

export default App;
