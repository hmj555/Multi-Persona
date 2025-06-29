import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "./Topic.css"; 
import topicsData from "../data/topics.json";

const Topics = () => {

  const navigate = useNavigate();
  const location = useLocation();

  // URL에서 participantId 가져오기
  const queryParams = new URLSearchParams(location.search);
  const participantId = queryParams.get("participantId") || "Unknown";
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://multi-personas-backend.onrender.com"; 

  useEffect(() => {
    console.log(`[INFO] 참가자 번호 확인: ${participantId}`);
  }, [participantId]);

  const [emotionalTopics, setEmotionalTopics] = useState([]);
  const [appraisalTopics, setAppraisalTopics] = useState([]);
  const [informationalTopics, setInformationalTopics] = useState([]);
  const [selectedEmotional, setSelectedEmotional] = useState([]);
  const [selectedAppraisal, setSelectedAppraisal] = useState([]);
  const [selectedInformational, setSelectedInformational] = useState([]);
  const [tooltip, setTooltip] = useState({ visible: false, text: "", x: 0, y: 0 });
  const [counterbalancedTopics, setCounterbalancedTopics] = useState(null);

  useEffect(() => {
    const emotional = topicsData.filter(topic => topic.index >= 1 && topic.index <= 25);
    const appraisal = topicsData.filter(topic => topic.index >= 26 && topic.index <= 50);
    const informational = topicsData.filter(topic => topic.index >= 51 && topic.index <= 76);

    setEmotionalTopics(emotional);
    setAppraisalTopics(appraisal);
    setInformationalTopics(informational);
  }, []);

  const handleCheckboxChange = (category, id) => {
    if (category === "Emotional Support") {
      if (selectedEmotional.includes(id)) {
        setSelectedEmotional(selectedEmotional.filter(item => item !== id));
      } else if (selectedEmotional.length < 6) {
        setSelectedEmotional([...selectedEmotional, id]);
      }
    } else if (category === "Appraisal Support") {
      if (selectedAppraisal.includes(id)) {
        setSelectedAppraisal(selectedAppraisal.filter(item => item !== id));
      } else if (selectedAppraisal.length < 6) {
        setSelectedAppraisal([...selectedAppraisal, id]);
      }
    } else if (category === "Informational Support") {
      if (selectedInformational.includes(id)) {
        setSelectedInformational(selectedInformational.filter(item => item !== id));
      } else if (selectedInformational.length < 6) {
        setSelectedInformational([...selectedInformational, id]);
      }
    }
  };

  const handleMouseEnter = (event, description) => {
    const rect = event.target.getBoundingClientRect(); // 요소의 위치 가져오기
    setTooltip({
      visible: true,
      text: description,
      x: rect.left + window.scrollX + 20, // 툴팁 위치 조정
      y: rect.top + window.scrollY + 30
    });
  };

  const handleMouseLeave = () => {
    setTooltip({ visible: false, text: "", x: 0, y: 0 });
  };

  // 배열을 랜덤하게 섞는 함수
  const shuffleArray = (array) => {
    return array.sort(() => Math.random() - 0.5);
  };



  // 카운터밸런싱 수행 함수
  const handleFinalizeSelection = async () => {
    if (selectedEmotional.length !== 6 || selectedAppraisal.length !== 6 || selectedInformational.length !== 6) {
      alert("각 카테고리에서 6개의 주제를 선택해야 합니다!");
      return;
    }

    const timestamp = new Date().toISOString(); // ✅ 현재 시간 기록

    // ✅ "선택 완료" 버튼 클릭 로그 서버로 전송
    try {
      await axios.post(`${BACKEND_URL}/log_event`, {
        participantId: participantId,
        page: "Topic",
        button: "선택 완료",
        timestamp: timestamp
      });
      console.log(`[LOG] "선택 완료" 버튼 클릭됨 - 시간: ${timestamp}`);
    } catch (error) {
      console.error("🚨 [ERROR] 버튼 클릭 로그 저장 실패:", error);
    }

    const selectedEmotionalTopics = topicsData.filter(topic => selectedEmotional.includes(topic.index));
    const selectedAppraisalTopics = topicsData.filter(topic => selectedAppraisal.includes(topic.index));
    const selectedInformationalTopics = topicsData.filter(topic => selectedInformational.includes(topic.index));

    const shuffledEmotional = shuffleArray([...selectedEmotionalTopics]);
    const shuffledAppraisal = shuffleArray([...selectedAppraisalTopics]);
    const shuffledInformational = shuffleArray([...selectedInformationalTopics]);

    const persona1Emotional = shuffledEmotional.slice(0, 3);
    const persona2Emotional = shuffledEmotional.slice(3, 6);
    const persona1Appraisal = shuffledAppraisal.slice(0, 3);
    const persona2Appraisal = shuffledAppraisal.slice(3, 6);
    const persona1Informational = shuffledInformational.slice(0, 3);
    const persona2Informational = shuffledInformational.slice(3, 6);

    const persona1Topics = shuffleArray([...persona1Emotional, ...persona1Appraisal, ...persona1Informational]);
    const persona2Topics = shuffleArray([...persona2Emotional, ...persona2Appraisal, ...persona2Informational]);

    const finalSelection = {
      tag_topics: persona1Topics.map(topic => topic.title_en),
      epi_topics: persona2Topics.map(topic => topic.title_en),
      // ✅ 추가
      tag_topic_descriptions: persona1Topics.map(topic => topic.description_en),
      epi_topic_descriptions: persona2Topics.map(topic => topic.description_en),
    };

    setCounterbalancedTopics(finalSelection);
    console.log("Counterbalanced Topics:", finalSelection);
    // 📝 FastAPI 서버로 데이터 저장 요청
    try {
      console.log("📡 [INFO] 서버로 선택된 토픽 데이터 전송 중...");
      const response = await axios.post(`${BACKEND_URL}/save_selected_topics/${participantId}`, finalSelection);
      console.log("✅ [SUCCESS] 선택된 토픽 저장 완료:", response.data);
      alert("주제 선택이 완료되었습니다!");
      
      // 🚀 다음 단계로 이동
      navigate(`/introper1?participantId=${participantId}`);

    } catch (error) {
      console.error("🚨 [ERROR] 선택된 토픽 저장 실패:", error.response?.data || error.message);
      alert("서버 요청 중 오류가 발생했습니다.");
    }
  };


  return (
    <div className="page-container">
    <div className="fixed-shape">
  <span>Evaluating the Chat Experience with a Self-representative Persona >> </span> <p>&nbsp; Topic Selection </p> {/* 아이콘 또는 텍스트 추가 가능 */}
  </div>


    <div className="topic-container">

      <section className="experiment-procedure">
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>각 카테고리에서 <strong>6개씩 주제</strong>를 <strong>선택</strong>해주세요.</p>
      <p>주제 위에 마우스를 올리면 주제에 대해 보다 <strong>상세한 설명</strong>이 나타납니다.</p>
      </section>

      <h2>Informational Support Topic</h2>
      <div className="category">
        {informationalTopics.map(topic => (
          <label 
            key={topic.index} 
            className={`checkboxLabel ${selectedInformational.includes(topic.index) ? "selected" : ""}`}
            onMouseEnter={(e) => handleMouseEnter(e, topic.description_en)}
            onMouseLeave={handleMouseLeave}
          >
            {/* 기존 체크박스를 숨김 */}
            <input
              type="checkbox"
              className="hidden-checkbox"
              checked={selectedInformational.includes(topic.index)}
              onChange={() => handleCheckboxChange("Informational Support", topic.index)}
            />
            
            {/* 제목 표시 */}
            <span className="topic-title">&nbsp;&nbsp;&nbsp;&nbsp;{topic.title_en}</span>

            {/* Select 버튼 (기본) */}
            <span className="select-button">
              {selectedInformational.includes(topic.index) ?  "Selected ✔️" : "Select +"}
            </span>
          </label>
        ))}
        <p className="selectionCount">Selected: {selectedInformational.length} / 6</p>
      </div>

      <h2>Emotional Support Topic</h2>
      <div className="category">
        {emotionalTopics.map(topic => (
          <label 
            key={topic.index} 
            className={`checkboxLabel ${selectedEmotional.includes(topic.index) ? "selected" : ""}`}
            onMouseEnter={(e) => handleMouseEnter(e, topic.description_en)}
            onMouseLeave={handleMouseLeave}
          >
            {/* 기존 체크박스를 숨김 */}
            <input
              type="checkbox"
              className="hidden-checkbox"
              checked={selectedEmotional.includes(topic.index)}
              onChange={() => handleCheckboxChange("Emotional Support", topic.index)}
            />

            {/* 제목 표시 */}
            <span className="topic-title">&nbsp;&nbsp;&nbsp;&nbsp;{topic.title_en}</span>

            {/* Select 버튼 (기본) */}
            <span className="select-button">
              {selectedEmotional.includes(topic.index) ? "Selected ✔️" : "Select +"}
            </span>
          </label>
        ))}
        <p className="selectionCount">Selected: {selectedEmotional.length} / 6</p>
      </div>

      <h2>Appraisal Support Topic</h2>
      <div className="category">
        {appraisalTopics.map(topic => (
          <label 
            key={topic.index} 
            className={`checkboxLabel ${selectedAppraisal.includes(topic.index) ? "selected" : ""}`}
            onMouseEnter={(e) => handleMouseEnter(e, topic.description_en)}
            onMouseLeave={handleMouseLeave}
          >
            {/* 기존 체크박스를 숨김 */}
            <input
              type="checkbox"
              className="hidden-checkbox"
              checked={selectedAppraisal.includes(topic.index)}
              onChange={() => handleCheckboxChange("Appraisal Support", topic.index)}
            />
            
            {/* 제목 표시 */}
            <span className="topic-title">&nbsp;&nbsp;&nbsp;&nbsp;{topic.title_en}</span>

            {/* Select 버튼 (기본) */}
            <span className="select-button">
              {selectedAppraisal.includes(topic.index) ?  "Selected ✔️" : "Select +"}
            </span>
          </label>
        ))}
        <p className="selectionCount">Selected: {selectedAppraisal.length} / 6</p>
      </div>



      <button
        className="submitButton"
        disabled={selectedEmotional.length !== 6 || selectedAppraisal.length !== 6 || selectedInformational.length !== 6}
        onClick={handleFinalizeSelection}
      >
        선택 완료
      </button>

      {counterbalancedTopics && (
        <div className="counterbalanced-results">
          {/* <h3>카운터밸런싱 결과</h3>
          <p><strong>Persona 1 주제:</strong> {counterbalancedTopics.persona1.join(", ")}</p>
          <p><strong>Persona 2 주제:</strong> {counterbalancedTopics.persona2.join(", ")}</p> */}
        </div>
      )}

      {tooltip.visible && (
        <div className="tooltip" style={{ top: tooltip.y + 15, left: tooltip.x +10,  maxWidth: "500px"}}>
          {tooltip.text}
        </div>
      )}
    </div>
    </div>
  );
};

export default Topics;
