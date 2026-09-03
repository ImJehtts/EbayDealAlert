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
    <div className="page">
      <div >
        <h1 style = {{ marginBottom: 0 }}>eBay Deal Finder</h1>
        <h2 style={{ fontWeight: "normal", fontSize: "1.75rem", marginBottom: "-1rem" }}>Get notified when eBay listings hit your price.</h2>
        <p>Demo mode — notification emails only send to pre-verified addresses. Use ebaydealfinderaws@gmail.com to create, list, and delete alerts</p>
        <section className="CreateAlertCard">
          <h2>Create an alert</h2>
          <label className="field">
            <span className="label">Keyword</span>
            <div className="row">
              <input
                type="text"
                placeholder="iPhone 6"
                value={keyword}
                onChange={(e) => {
                  setKeyword(e.target.value);
                  setCategoryId("");
                  setCategories([]);
                }}
              />
              <button className = "btn-secondary" onClick={findCategories}>Find categories</button>
            </div>
          </label>
          {categories.length > 0 && (
            <label className="field">
              <span className="label">Category <span className="optional">(optional)</span></span>
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
            </label>
          )}

          <label className="field">
            <span className="label">Notify this email</span>
            <input
              type="email"
              placeholder="ebaydealfinderaws@gmail.com"
              value={email}
              onChange={(e) => setEmail(e.target.value.toLowerCase())}
            />
          </label>

          <label className="field">
            <span className="label">Max price (CAD)</span>
            <input
              type="number"
              placeholder="400"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
            />
          </label>

          <button className = "btn-primary" onClick={createAlert}>Create Alert</button>
          {status && <p>{status}</p>}
        </section>
      </div>
      
      <div>
        <section className="ListDeleteCard">
          <h2>List & Delete Alerts</h2>
          <div className="row">
            <input
              type="email"
              placeholder="ebaydealfinderaws@gmail.com"
              value={lookupEmail}
              onChange={(e) => setLookupEmail(e.target.value)}
            />
            <button className="btn-secondary" onClick={loadAlerts}>Load Alerts</button>
            </div>
            {alerts.length === 0 ? (
              <p className="empty">
                No alerts yet - enter an email above and we'll list all relevant alerts.
              </p>
            ) : (
              alerts.map((alert) => (
                <div className="alert-row" key={alert.alertId}>
                  <div>
                  <strong>{alert.keyword}</strong>
                    <div className="alert-details">
                      <span> Under ${alert.maxPrice} {alert.currency}</span>
                      {alert.categoryName && <span> · {alert.categoryName}</span>}
                    </div>
                  </div>
                  <button className = "btn-delete" 
                    onClick={() => deleteAlert(alert.alertId)}>
                    Delete
                  </button>
                </div>
              ))
            )}
        </section>
        </div>
      </div>
  );
}