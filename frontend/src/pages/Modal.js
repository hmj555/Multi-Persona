import React from "react";
import "./Modal.css"; // ✅ 모달 스타일 

const Modal = ({ isOpen, onClose, surveyQuestions, surveyResponses, handleSurveyChange, handleSurveySubmit }) => {
  console.log("[DEBUG] isOpen 상태:", isOpen); // ✅ 모달이 열릴 때 상태 확인

  if (!isOpen) return null; // ✅ isOpen이 false면 모달 숨김

  // ✅ 모든 설문 응답 확인
  const validateSurvey = () => {
    const unansweredQuestions = surveyQuestions
      .map((_, index) => `Q${index + 1}`)
      .filter((key) => !surveyResponses[key]); // 응답이 없는 질문 찾기

    if (unansweredQuestions.length > 0) {
      alert("모든 문항에 응답하지 않았습니다.");
      return false; // ✅ 제출 방지
    }
    return true;
  };

  // ✅ 응답 확인 후 제출 실행
  const handleSubmit = () => {
    if (validateSurvey()) {
      handleSurveySubmit();
    }
  };


  return (
    <div className="chat-modal-container">
      <div className="chat-modal-container-header">
        <h2 className="chat-modal-container-title" style={{ color: "#ffffff" }}> Chat Experience Evaluation </h2>
        <button className="icon-button" onClick={onClose}>
          <svg width="20" height="20" viewBox="0 0 24 24" strokeWidth="1.5" stroke="#000" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div className="chat-modal-container-body">
        {surveyQuestions.map((question, index) => (
          <div key={index} className="modal-survey-question">
            <p style={{ color: "#ffffff", fontSize: "14.5px", fontWeight: "bold"}} >Q{index + 1}. {question}</p>
            <div className="modal-scale-container">
              <span className="modal-scale-label">Strongly <br></br>Disagree</span>
              {[1, 2, 3, 4, 5, 6, 7].map((num) => (
                <label key={num} className="modal-scale-option">
                  <input
                    type="radio"
                    name={`Q${index + 1}`}
                    value={num}
                    checked={surveyResponses[`Q${index + 1}`] === num}
                    onChange={() => handleSurveyChange(`Q${index + 1}`, num)}
                  />
                  {num}
                </label>
              ))}
              <span className="modal-scale-label">Stronly <br></br> Agree</span>
            </div>
          </div>
        ))}
      </div>
      <div className="chat-modal-container-footer">
        <button className="modal-button is-primary" onClick={handleSubmit}>Submit</button>
      </div>
    </div>
  );
};

export default Modal;
