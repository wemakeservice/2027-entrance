import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { Search, MapPin, BookOpen, CheckCircle, XCircle, FileText, ArrowRightLeft, X } from 'lucide-react';
import { University } from './types';

function App() {
  const [data, setData] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [search, setSearch] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('전체');
  const [selectedType, setSelectedType] = useState('전체');
  const [hasMinScore, setHasMinScore] = useState('전체');
  const [hasInterview, setHasInterview] = useState('전체');

  // Compare State
  const [compareList, setCompareList] = useState<University[]>([]);
  const [showCompareModal, setShowCompareModal] = useState(false);

  useEffect(() => {
    axios.get('http://localhost:8000/api/universities')
      .then(res => {
        setData(res.data.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Data fetch error:', err);
        setLoading(false);
      });
  }, []);

  const regions = useMemo(() => ['전체', ...Array.from(new Set(data.map(d => d.지역))).filter(Boolean).sort()], [data]);
  const types = useMemo(() => ['전체', ...Array.from(new Set(data.map(d => d.전형유형))).filter(Boolean).sort()], [data]);

  const filteredData = useMemo(() => {
    return data.filter(uni => {
      if (search && !uni.대학명.includes(search)) return false;
      if (selectedRegion !== '전체' && uni.지역 !== selectedRegion) return false;
      if (selectedType !== '전체' && uni.전형유형 !== selectedType) return false;
      if (hasMinScore !== '전체' && uni.수능최저 !== hasMinScore) return false;
      if (hasInterview !== '전체' && uni.면접 !== hasInterview) return false;
      return true;
    });
  }, [data, search, selectedRegion, selectedType, hasMinScore, hasInterview]);

  const toggleCompare = (uni: University) => {
    if (compareList.find(u => u.대학명 === uni.대학명)) {
      setCompareList(prev => prev.filter(u => u.대학명 !== uni.대학명));
    } else {
      if (compareList.length >= 3) {
        alert("비교는 최대 3개 대학까지만 가능합니다.");
        return;
      }
      setCompareList(prev => [...prev, uni]);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1><Search size={24} /> 2027 대입 시행계획 네비게이터</h1>
        <p>전국 196개 주요 대학의 전형 조건을 한눈에 비교하세요</p>
      </header>

      <main className="main-content">
        <aside className="filter-panel">
          <div className="filter-group">
            <h3>대학명 검색</h3>
            <input 
              type="text" 
              className="filter-select"
              placeholder="예: 서울대학교" 
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <h3><MapPin size={16} style={{display:'inline', verticalAlign:'text-bottom'}}/> 지역</h3>
            <select className="filter-select" value={selectedRegion} onChange={e => setSelectedRegion(e.target.value)}>
              {regions.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>

          <div className="filter-group">
            <h3><BookOpen size={16} style={{display:'inline', verticalAlign:'text-bottom'}}/> 전형 유형</h3>
            <select className="filter-select" value={selectedType} onChange={e => setSelectedType(e.target.value)}>
              {types.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div className="filter-group">
            <h3>수능최저학력기준</h3>
            <div className="radio-group">
              {['전체', '있음', '없음'].map(opt => (
                <label key={opt} className="radio-label">
                  <input type="radio" name="csat" value={opt} checked={hasMinScore === opt} onChange={() => setHasMinScore(opt)} />
                  {opt}
                </label>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <h3>면접 유무</h3>
            <div className="radio-group">
              {['전체', '있음', '없음'].map(opt => (
                <label key={opt} className="radio-label">
                  <input type="radio" name="interview" value={opt} checked={hasInterview === opt} onChange={() => setHasInterview(opt)} />
                  {opt}
                </label>
              ))}
            </div>
          </div>
        </aside>

        <section className="results-area">
          {loading ? (
            <div style={{textAlign:'center', padding:'3rem', color:'#64748B'}}>데이터를 불러오는 중입니다...</div>
          ) : (
            <>
              <div className="results-header">
                <div className="results-count">검색 결과 <span>{filteredData.length}</span>개 대학</div>
              </div>
              
              <div className="card-grid">
                {filteredData.map(uni => {
                  const isSelected = compareList.some(u => u.대학명 === uni.대학명);
                  return (
                    <div key={uni.대학명} className="uni-card">
                      <div className="uni-card-header">
                        <h2 className="uni-name">{uni.대학명}</h2>
                        <span className="uni-region">{uni.지역}</span>
                      </div>
                      
                      <div className="uni-details">
                        <span className="detail-badge neutral">{uni.전형유형}</span>
                        <span className={`detail-badge ${uni.수능최저 === '있음' ? 'warning' : 'neutral'}`}>
                          {uni.수능최저 === '있음' ? <CheckCircle size={14}/> : <XCircle size={14}/>} 
                          수능최저 {uni.수능최저}
                        </span>
                        <span className={`detail-badge ${uni.면접 === '있음' ? 'warning' : 'neutral'}`}>
                          {uni.면접 === '있음' ? <CheckCircle size={14}/> : <XCircle size={14}/>}
                          면접 {uni.면접}
                        </span>
                      </div>
                      
                      <div className="uni-actions">
                        <button 
                          className={`btn ${isSelected ? 'btn-outline selected' : 'btn-outline'}`}
                          onClick={() => toggleCompare(uni)}
                        >
                          {isSelected ? '비교 해제' : '+ 비교 담기'}
                        </button>
                        {uni.drive_url ? (
                          <a href={uni.drive_url} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
                            <FileText size={16} /> 모집요강 보기
                          </a>
                        ) : (
                          <button className="btn btn-disabled" disabled>
                            링크 없음
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              {filteredData.length === 0 && (
                <div style={{textAlign:'center', padding:'3rem', color:'#64748B'}}>
                  조건에 맞는 대학이 없습니다. 필터를 변경해 보세요.
                </div>
              )}
            </>
          )}
        </section>
      </main>

      {/* Floating Compare Tray */}
      <div className={`compare-tray ${compareList.length > 0 ? 'visible' : ''}`}>
        <div className="tray-content">
          <div className="selected-list">
            {compareList.map(uni => (
              <div key={uni.대학명} className="selected-item">
                {uni.대학명}
                <button onClick={() => toggleCompare(uni)}><X size={14}/></button>
              </div>
            ))}
          </div>
          <button 
            className="btn btn-primary" 
            style={{width: 'auto', padding: '0.75rem 1.5rem'}}
            onClick={() => setShowCompareModal(true)}
            disabled={compareList.length < 2}
          >
            <ArrowRightLeft size={16} /> 
            {compareList.length < 2 ? '2개 이상 담아주세요' : '선택 대학 비교하기'}
          </button>
        </div>
      </div>

      {/* Compare Modal */}
      {showCompareModal && (
        <div className="modal-overlay" onClick={() => setShowCompareModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>대학 전형 조건 비교</h2>
              <button className="close-btn" onClick={() => setShowCompareModal(false)}><X size={24}/></button>
            </div>
            
            <div style={{overflowX: 'auto'}}>
              <table className="compare-table">
                <thead>
                  <tr>
                    <th>구분</th>
                    {compareList.map(uni => <th key={uni.대학명} style={{color: '#1E3A8A', fontSize: '1.125rem'}}>{uni.대학명}</th>)}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>지역</td>
                    {compareList.map(uni => <td key={uni.대학명}>{uni.지역}</td>)}
                  </tr>
                  <tr>
                    <td>주요 전형유형</td>
                    {compareList.map(uni => <td key={uni.대학명}>{uni.전형유형}</td>)}
                  </tr>
                  <tr>
                    <td>수능최저학력기준</td>
                    {compareList.map(uni => (
                      <td key={uni.대학명} style={{color: uni.수능최저 === '있음' ? '#D97706' : '#64748B'}}>
                        {uni.수능최저}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>면접 유무</td>
                    {compareList.map(uni => (
                      <td key={uni.대학명} style={{color: uni.면접 === '있음' ? '#D97706' : '#64748B'}}>
                        {uni.면접}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>내신 반영 비율</td>
                    {compareList.map(uni => <td key={uni.대학명}>{uni.내신반영}</td>)}
                  </tr>
                  <tr>
                    <td>원본 PDF</td>
                    {compareList.map(uni => (
                      <td key={uni.대학명}>
                        {uni.drive_url ? (
                           <a href={uni.drive_url} target="_blank" rel="noopener noreferrer" style={{color: '#3B82F6', textDecoration: 'none'}}>
                             바로가기 ↗
                           </a>
                        ) : '-'}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
