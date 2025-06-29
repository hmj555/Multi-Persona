import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "./EpiEval.css"; 

const EpiEval = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const participantId = queryParams.get("participantId") || "Unknown";

  // ✅ 평가할 항목 (현실성, 일치성, 유용성, 다양성)
  const evaluationCriteria = [
    "Q1. This experience is likely to occur in real life.",
    "Q2. This experience helps represent who I am.",
    "Q3. This experience is  ",
    "Q4. In relation to my roles, I have had similar experiences to this one.",
  ];

  // ✅ 에피소드 및 기존 경험 데이터 저장할 상태
  const [episodes, setEpisodes] = useState([]);
  const [surveyResponses, setSurveyResponses] = useState({});
  const [identityData, setIdentityData] = useState([]); // 🔥 배열로 저장
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://multi-personas-backend.onrender.com"; 


  // ✅ 기존 경험 데이터 가져오기
  useEffect(() => {
    const fetchIdentityData = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/get_identity/${participantId}`);
        console.log("📌 Fetched Identity Data:", response.data.Identities);

        // 🔥 객체를 배열로 변환
        const identityArray = Object.entries(response.data.Identities).map(([role, details]) => ({
          role,
          experiences: [details.Ep1, details.Ep2].filter(Boolean), // Ep1, Ep2만 배열로 저장
        }));

        setIdentityData(identityArray);
      } catch (error) {
        console.error("🚨 [ERROR] 기존 경험 데이터 불러오기 실패:", error);
        setIdentityData([]); // 🔥 404 발생 시 빈 배열 할당
      }
    };

    fetchIdentityData();
  }, [participantId]);

  // ✅ 백엔드에서 에피소드 데이터 가져오기
  useEffect(() => {
    const fetchEpisodes = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/get_experiencable/${participantId}`);
        console.log("📌 Fetched Experiencable Data:", response.data.Experiencable);

        const experiencableData = response.data.Experiencable;

        if (experiencableData) {
          // ✅ 에피소드 데이터를 하나의 배열로 변환
          const formattedEpisodes = Object.entries(experiencableData).flatMap(([category, episodes]) =>
            episodes.map((episode, index) => ({
              category, // "공상가", "시골 출생자", "첫째딸" 등의 Role
              title: `에피소드 ${index + 1}`,
              content: episode
            }))
          );

          setEpisodes(formattedEpisodes);
        }
      } catch (error) {
        console.error("🚨 [ERROR] 에피소드 데이터 불러오기 실패:", error);
      }
    };

    fetchEpisodes();
  }, [participantId]);

  // ✅ 설문 응답 변경 핸들러
  const handleSurveyChange = (episodeIndex, criterion, value) => {
    setSurveyResponses((prev) => ({
      ...prev,
      [`${episodeIndex}_${criterion}`]: value,
    }));
  };

  // ✅ 제출 버튼 클릭 시 실행
  // const handleSubmit = async () => {
  //   // ✅ 모든 질문에 대한 응답 확인
  //   const unansweredQuestions = episodes.flatMap((_, episodeIndex) =>
  //     evaluationCriteria.map((criterion) => `${episodeIndex}_${criterion}`)
  //   ).filter((key) => !surveyResponses[key]);
  
  //   if (unansweredQuestions.length > 0) {
  //     alert("모든 문항에 응답하지 않았습니다.");
  //     return; // ✅ 페이지 이동 방지
  //   }
  
  //   try {
  //     await axios.post("http://127.0.0.1:8000/submit_epi_eval", {
  //       user_number: participantId,
  //       responses: surveyResponses,
  //     });
  
  //     alert("설문이 제출되었습니다!");
  //     navigate(`/final?participantId=${participantId}`);
  //   } catch (error) {
  //     console.error("🚨 [ERROR] 설문 제출 실패:", error);
  //   }
  // };

  const handleSubmit = async () => {
    // ✅ 모든 질문에 대한 응답 확인
    const unansweredQuestions = episodes.flatMap((_, episodeIndex) =>
      evaluationCriteria.map((criterion) => `${episodeIndex}_${criterion}`)
    ).filter((key) => !surveyResponses[key]);
  
    if (unansweredQuestions.length > 0) {
      alert("모든 문항에 응답하지 않았습니다.");
      return; // ✅ 페이지 이동 방지
    }
  
    const timestamp = new Date().toISOString(); // 현재 시간 기록
  
    try {
      // ✅ 설문 응답 로깅 (FastAPI `/log_survey` 호출)
      await axios.post(`${BACKEND_URL}/log_survey`, {
        participantId: participantId,
        page: "EpiEval",
        timestamp: timestamp,
        responses: surveyResponses,
      });
  
      console.log(`[LOG] 에피소드 설문 응답 저장됨 - 시간: ${timestamp}, 응답:`, surveyResponses);
  
      // ✅ 버튼 클릭 이벤트 로깅 (FastAPI `/log_event` 호출)
      await axios.post(`${BACKEND_URL}/log_event`, {
        participantId: participantId,
        page: "EpiEval",
        button: "제출하기",
        timestamp: timestamp,
      });
  
      console.log(`[LOG] 제출하기 버튼 클릭 - 시간: ${timestamp}`);
  
      alert("설문이 제출되었습니다!");
  
      // ✅ 다음 페이지로 이동
      navigate(`/final?participantId=${participantId}`);
    } catch (error) {
      console.error("🚨 [ERROR] 설문 응답 또는 로그 저장 실패:", error);
    }
  };

  return (
    <div className="page-container">
      <div className="fixed-shape">
        <span> >> Chat with Persona 2 and Experience Evaluation >> Persona 2 Evaluation >> </span> 
        <p>&nbsp; Augmented Experiences Evaluation </p> 
      </div>

      <div className="epieval-container">
        <div className="chat-topic">
          <div className="epi-content">📘 Augmented Experiences Evaluation</div>          
        </div>
        <hr className="epi-divider" />
        <p></p>
        {/* <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        아래의 6가지 에피소드를 읽고 문항에 따라 평가해주세요. <br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            *<span className="epieval-highlight-tooltip">기존 경험</span>에서 세부 정보는 재표현 되었습니다. (예: '무안' -> '시골 마을' )</p> */}

        {episodes.length > 0 ? (
          <div className="epieval-body">
            {episodes.map((episode, episodeIndex) => {
              // 🔥 identityData에서 해당 role(공상가, 시골 출생자 등) 찾기
              const matchedIdentity = identityData.find(identity => identity.role === episode.category);

              return (
                <div key={episodeIndex} className="episode-wrapper">
                  
                  {/* ✅ 에피소드 내용 */}
                  <div className="episode-container">
                    <h3> '{episode.category}'의 {episode.title}</h3>
                    <p className="episode-content">{episode.content}</p>
                  </div>

                  {/* ✅ 설문 질문 */}
                  <div className="survey-container">
                    {evaluationCriteria.map((criterion, index) => (
                      <div key={`${episodeIndex}_${criterion}`} className="episurvey-question">
                        <section className="experiment-procedure">
                          <p className="epieval-criterion-label">
                            <strong>
                              {index === 2 ? (
                                <>
                                  Q3. This experience is distinct from my previously{" "}
                                  <span className="epieval-highlight-tooltip">
                                    provided experiences.
                                    <span className="epieval-tooltip">
                                    {matchedIdentity
                                        ? matchedIdentity.experiences.map((exp, index) => (
                                            <React.Fragment key={index}>
                                            {exp}
                                            <br />
                                            <br /> 
                                            </React.Fragment>
                                        ))
                                        : "데이터 없음"}
                                        
                                    </span>
                                  </span>
                                  
                                </>
                              ) : (
                                criterion
                              )}
                            </strong>
                          </p>
                        </section>
                        <div className="epieval-scale-container">
                          <span className="epieval-scale-label">Strongly <br></br>Disagree</span>
                          {[1, 2, 3, 4, 5, 6, 7].map((num) => (
                            <label key={num} className="epieval-scale-option">
                              <input
                                type="radio"
                                name={`${episodeIndex}_${criterion}`}
                                value={num}
                                checked={surveyResponses[`${episodeIndex}_${criterion}`] === num}
                                onChange={() => handleSurveyChange(episodeIndex, criterion, num)}
                              />
                              {num}
                            </label>
                          ))}
                          <span className="epieval-scale-label">Strongly <br></br>Agree</span>
                        </div>
                      </div>
                    ))}
                  </div>

                </div>
              );
            })}
          </div>
        ) : (
          <p>⏳ 에피소드 데이터를 불러오는 중...</p>
        )}
        
        <button className="button submit-button" onClick={handleSubmit}>
          Submit
        </button>
      </div>
    </div>
  );
};

export default EpiEval;
