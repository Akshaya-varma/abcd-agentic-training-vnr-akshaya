import React from "react";

function NewsCard({ article }) {
  return (
    <div style={{ border: "1px solid #ccc", margin: "1rem 0", padding: "1rem" }}>
      <h3>{article.title}</h3>
      {article.urlToImage && (
        <img
          src={article.urlToImage}
          alt={article.title}
          style={{ width: "100%", maxHeight: "300px", objectFit: "cover" }}
        />
      )}
      <p>{article.description}</p>
      <p><strong>Source:</strong> {article.source.name}</p>
      <a href={article.url} target="_blank" rel="noopener noreferrer">
        Read More →
      </a>
    </div>
  );
}




export default NewsCard;
