import { useState } from "react";

const API = import.meta.env.VITE_API_URL;

export default function App() {
  //Create Alerts useState variables 
  const [keyword, setKeyword] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");

  //List & Delete Alerts useState variables
  const [alerts, setAlerts] = useState([]);
  const [lookupEmail, setLookupEmail] = useState("");

  //Category useState variable
  const [categories, setCategories] = useState([]);
  const [categoryId, setCategoryId] = useState("");

  const createAlert = async () => {
    if (!keyword || !maxPrice || !email) {
    setStatus("Keyword, max price, and email are all required.");
    return;
    }
    const body = { email, keyword, maxPrice: Number(maxPrice) };
      if (categoryId) {
        const chosen = categories.find((c) => c.categoryId === categoryId);
        body.categoryId = categoryId;
        body.categoryName = chosen ? chosen.categoryName : "";
    }
    setStatus("Creating alert...");
    try {
      const response = await fetch(`${API}/alerts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        setStatus(`Error: ${data.error || response.status}`);
        return;
      }

      setStatus(`Created ${data.alertId}`);
      setKeyword("");
      setMaxPrice("");
      setCategories([]);
      setCategoryId("");

    } catch (err) {
      setStatus(`Error: ${err.message}`);
    }
  };

  const loadAlerts = async () => {
      try {
        const response = await fetch(`${API}/alerts?email=${encodeURIComponent(lookupEmail)}`);
        const data = await response.json();
        if (!response.ok) {
          setStatus(`Error: ${data.error || response.status}`);
          return;
        }
      setAlerts(data.alerts);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    }
  };

  const deleteAlert = async (alertId) => {
    try {
      const response = await fetch(
        `${API}/alerts/${alertId}?email=${encodeURIComponent(lookupEmail)}`,
        { method: "DELETE" }
      );
      if (!response.ok) {
        const data = await response.json();
        setStatus(`Error: ${data.error || response.status}`);
        return;
      }
      loadAlerts();
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    }
  };

  const findCategories = async () => {
  if (!keyword) {
    setStatus("Enter a keyword first.");
    return;
  }
  setStatus("Finding categories...");
  try {
    const response = await fetch(
      `${API}/categories?q=${encodeURIComponent(keyword)}`
    );
    const data = await response.json();
    if (!response.ok) {
      setStatus(`Error: ${data.error || response.status}`);
      return;
    }
    setCategories(data.categories);
    //Reset the selected category ID when new categories are loaded
    setCategoryId("");
    setStatus(`${data.categories.length} categories found.`);
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
};

  return (
    <>
      <div style={{ padding: 24, maxWidth: 480, fontFamily: "system-ui" }}>
        <h1>eBay Deal Finder</h1>
        <p>Due to my AWS SES being in sandbox environment, please use the email: ebaydealfinderaws@gmail.com to create, list, and delete alerts</p>
        <input
          type="text"
          placeholder="Keyword"
          value={keyword}
          onChange={(e) => {
            setKeyword(e.target.value);
            setCategoryId("");
            setCategories([]);
          }}
        />
        <button onClick={findCategories}>Find categories</button>

        {categories.length > 0 && (
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
          >
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c.categoryId} value={c.categoryId}>
                {c.categoryName} ({c.matchCount.toLocaleString()})
              </option>
            ))}
          </select>
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        
        <input
          type="number"
          placeholder="Max Price"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />
        <button onClick={createAlert}>Create Alert</button>
        {status && <p>{status}</p>}
      </div>
      <div style={{ padding: 24, maxWidth: 480, fontFamily: "system-ui" }}>
        <h1>List & Delete Alerts</h1>
        <input
          type="email"
          placeholder="Email"
          value={lookupEmail}
          onChange={(e) => setLookupEmail(e.target.value)}
        />
        <button onClick={loadAlerts}>Load Alerts</button>
        {alerts.length === 0 ? (
          <p>No alerts yet - enter an email above and we'll list all relevant alerts.</p>
        ) : (
          alerts.map((alert) => (
            <div key={alert.alertId}>
              <strong>{alert.keyword}</strong>
              <span> Under ${alert.maxPrice} {alert.currency}</span>
              {alert.categoryName && <span> · {alert.categoryName}</span>}
              <button onClick={() => deleteAlert(alert.alertId)}>Delete</button>
            </div>
          ))
        )}
      </div>
    </>
  );
}