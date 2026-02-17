import React, { useState, useEffect } from 'react';

export default function WhaleMonitor() {
  const [signals, setSignals] = useState([]);
  const [count, setCount] = useState(0);

  useEffect(() => {
    const fetchSignals = async () => {
      try {
        const res = await fetch('http://localhost:5001/api/whale-signals?limit=20');
        const data = await res.json();
        setSignals(data.signals);
        setCount(data.total);
      } catch (e) {
        console.log('Bot not running');
      }
    };
    
    fetchSignals();
    const interval = setInterval(fetchSignals, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '20px', background: '#1a1a1a', color: '#fff', fontFamily: 'Arial' }}>
      <h1>🐋 Whale Monitor - Total Signals: {count}</h1>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px', background: '#2a2a2a' }}>
        <thead>
          <tr style={{ background: '#333' }}>
            <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Symbol</th>
            <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Price</th>
            <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Action</th>
            <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Confidence</th>
            <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #444' }}>Time</th>
          </tr>
        </thead>
        <tbody>
          {signals.slice().reverse().map(s => {
            const color = s.action === 'BUY' ? '#10b981' : s.action === 'SELL' ? '#ef4444' : '#f59e0b';
            const emoji = s.action === 'BUY' ? '🚀' : s.action === 'SELL' ? '📉' : '➡️';
            
            return (
              <tr key={s.id} style={{ borderBottom: '1px solid #444' }}>
                <td style={{ padding: '12px' }}><b>{s.symbol}</b></td>
                <td style={{ padding: '12px' }}>${s.price?.toFixed(2)}</td>
                <td style={{ padding: '12px', color: color, fontWeight: 'bold' }}>{emoji} {s.action}</td>
                <td style={{ padding: '12px' }}>{(s.confidence * 100)?.toFixed(0)}%</td>
                <td style={{ padding: '12px', fontSize: '12px', color: '#999' }}>{new Date(s.timestamp).toLocaleTimeString()}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
