const API_KEY = process.env.REACT_APP_NEWS_API_KEY;

export const fetchNews = async (query = "technology") => {
  const url = `https://newsapi.org/v2/everything?q=${query}&apiKey=${API_KEY}`;
  console.log("Fetching URL:", url);
  const res = await fetch(url);
  const data = await res.json();
  console.log("API response:", data);
  return data.articles ?? [];
};

