import React, { useState, useEffect } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import "./Chat.css";
import Modal from "./Modal"; // 모달 스타일 추가


const Chat2 = () => {
  const navigate = useNavigate(); 
  const { chatId } = useParams();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const participantId = queryParams.get("participantId") || "Unknown";

  const [topic, setTopic] = useState("");
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false); 
  const [surveyResponses, setSurveyResponses] = useState({});
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://multi-personas-backend.onrender.com"; 


  useEffect(() => {
    if (isModalOpen) {
      const modalBody = document.querySelector(".chat-modal-container-body");
      if (modalBody) {
        modalBody.scrollTop = 0; // ✅ 모달 열릴 때 스크롤을 최상단으로 초기화
      }
    }
  }, [isModalOpen]); 
  
      // ✅ 새로운 페이지마다 메시지 초기화
      useEffect(() => {
        console.log("📌 [DEBUG] chatId 변경됨, 메시지 초기화:", `chat2/${chatId}`);
        setMessages([]);  // ✅ 페이지 전환 시 기존 메시지 초기화
        setInputText("");
      }, [chatId]);  // chatId가 변경될 때마다 실행
    
      // ✅ 새로운 세션 ID 생성
      const session_id = `chat2/${chatId}`;
      // const session_id = `chat2_${participantId}/${chatId}`;


  const [isTopicLoaded, setIsTopicLoaded] = useState(false);

  // ✅ 주제 가져오기
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/get_user_topics/${participantId}`); // ✅ 문자열 템플릿 수정
        const topics = response.data.epi_topics;

        if (topics && chatId >= 1 && chatId <= topics.length) {
          console.log("📌 [DEBUG] 토픽 업데이트됨:", topics[chatId - 1]); // ✅ 디버깅 추가
          setTopic(topics[chatId - 1]);
          setIsTopicLoaded(true);
        } else {
          setTopic("자유 주제");
          setIsTopicLoaded(true); 
        }
      } catch (error) {
        console.error("🚨 [ERROR] 토픽 불러오기 실패:", error);
      }
    };

    if (chatId && participantId) {
      fetchTopics();
    }
  }, [chatId, participantId]);

  const sendMessage = async () => {
    if (!inputText.trim() || isSending || !isTopicLoaded) return; // ✅ 전송 중이면 실행 방지
    setIsSending(true); // ✅ 전송 시작
    console.log("📌 [DEBUG] 현재 토픽:", topic); // ✅ 확인용

    const session_id = `chat2/${chatId}`;
    const userMessage = { role: "user", content: inputText };

    setInputText(""); // 입력 필드 초기화
    setMessages((prev) => [...prev, userMessage]);

    try {
        // ✅ FastAPI 서버에 스트리밍 요청
        console.log("✅ Sending request to /chat_epi_stream:", {
            user_number: participantId,
            session_id: session_id,
            persona_type: "Epi",
            input_text: inputText,
            topic: topic,
            timestamp: new Date().getTime(), // ✅ 캐싱 방지
        });

        const response = await fetch(`${BACKEND_URL}/chat_epi_stream`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_number: participantId,
                session_id: session_id,
                persona_type: "Epi",
                input_text: inputText,
                topic: topic,
                timestamp: new Date().getTime(),
            }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiMessage = { role: "ai", content: "" };

        // ✅ AI 메시지를 실시간으로 추가
        setMessages((prev) => [...prev, aiMessage]);

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            aiMessage.content += decoder.decode(value, { stream: true });

            // ✅ 메시지를 실시간으로 업데이트
            setMessages((prev) => {
                const updatedMessages = [...prev];
                updatedMessages[updatedMessages.length - 1] = { ...aiMessage };
                return updatedMessages;
            });

            await new Promise((resolve) => setTimeout(resolve, 25)); // ✅ 속도 조절
        }

        console.log("✅ [DEBUG] 최종 AI 메시지:", aiMessage);
    } catch (error) {
        console.error("🚨 [ERROR] 메시지 전송 실패:", error);
    }
    setInputText("");
    setIsSending(false); // ✅ 전송 완료 후 다시 입력 가능하게 설정
};

  // const sendMessage = async () => {
  //   if (!inputText.trim() || isSending || !isTopicLoaded) return; // ✅ 전송 중이면 실행 방지
  //   setIsSending(true); // ✅ 전송 시작
  //   console.log("📌 [DEBUG] 현재 토픽:", topic); // ✅ 확인용

  //   const session_id = `chat2/${chatId}`;

  //   const userMessage = { role: "user", content: inputText };

  //   setInputText(""); // 입력 필드 초기화
  //   setMessages((prev) => [...prev, userMessage]);

  //   try {
  //     // ✅ FastAPI 서버에 메시지 전송
  //     console.log("✅ Sending request to /chat:", {
  //       user_number: participantId,
  //       session_id: session_id,
  //       persona_type: "Epi",
  //       input_text: inputText,
  //       topic: topic,  // ✅ 강제 토픽 전달
  //       timestamp: new Date().getTime(),  // ✅ 캐싱 방지
  //     });
  //     const response = await axios.post("http://127.0.0.1:8000/chat_epi", {
  //       user_number: participantId,
  //       session_id: session_id,
  //       persona_type: "Epi",
  //       input_text: inputText,
  //       topic: topic,
  //       timestamp: new Date().getTime(),
  //     });
  //     setInputText(""); // 입력 필드 초기화
  //     console.log("✅ Response data:", response.data);

  //     if (response.data && response.data.response) {
  //       const botMessage = { role: "ai", content: response.data.response };
  //       // setMessages((prev) => [...prev, botMessage]);
  //       setMessages(prevMessages => {
  //         console.log("📌 [DEBUG] 기존 messages:", prevMessages);
  //         console.log("📌 [DEBUG] 추가할 ai-message:", botMessage);
  //         return [...prevMessages, botMessage];
  //       });
  //     } else {
  //       console.error("🚨 [ERROR] No response content:", response.data);
  //     }
  //   } catch (error) {
  //     console.error("🚨 [ERROR] 메시지 전송 실패:", error);
  //   }
  //   setInputText(""); // 입력 필드 초기화
  //   setIsSending(false); // ✅ 전송 완료 후 다시 입력 가능하게 설정
  // };

  const surveyQuestions = [
    "나는 이 대화에 만족한다",
    "나는 이 대화에 몰입했다",
    "나는 이 대화가 흥미로웠다",
    "이 대화는 실제 사람과 이야기 나누는 것처럼 느꼈다",
    "이 대화는 토픽에 대해 적절하고 유용한 지원을 제공했다",
    "대화의 응답은 유연하며 기계적이지 않다",
    "대화의 응답은 간결하고 명확하다",
    "대화의 응답은 완전하다"
  ];

  const endConversation = async () => {
    if (messages.length === 0) {
      alert("대화 내용이 없습니다.");
      return;
    }

    const timestamp = new Date().toISOString(); // 현재 시간 기록

    try {
      await axios.post(`${BACKEND_URL}/save_chat_log`, {
        user_number: participantId,
        session_id: `${participantId}_chat`,
        persona_type: "Epi",
        messages: messages,
      });

    
        // ✅ 버튼 클릭 이벤트 로깅 추가
      await axios.post(`${BACKEND_URL}/log_event`, {
        participantId: participantId,
        page: `chat2(epi)/${chatId}`, // 현재 페이지 ID 포함
        button: "대화 종료", // 버튼 이름
        timestamp: timestamp,
      });

      console.log(`[LOG] 대화 종료 이벤트 저장 - 시간: ${timestamp}, 채팅 ID: chat2/${chatId}`);

      setIsModalOpen(true); // ✅ 모달 열기
      // alert("대화가 저장되었습니다."); 
      setMessages([]); // ✅ 대화 초기화
    } catch (error) {
      console.error("🚨 [ERROR] 대화 저장 실패:", error);
    }
  };

  // ✅ 설문 응답 변경 핸들러
  const handleSurveyChange = (question, value) => {
    setSurveyResponses((prev) => ({ ...prev, [question]: value }));
  };

  // const handleSurveySubmit = () => {
  //   setSurveyResponses({}); 
  //   setIsModalOpen(false); // ✅ 모달 닫기

  //   if (parseInt(chatId) === 10) {
  //     // ✅ 7번째 대화 후 PerEval 페이지로 이동
  //     navigate(`/pereval/epi?participantId=${participantId}`);
  //   } else {
  //     // ✅ 다음 대화로 이동
  //     const nextChatId = parseInt(chatId) + 1;
  //     navigate(`/chat2/${nextChatId}?participantId=${participantId}`);
  //   }
  // };


  // const handleSurveySubmit = async () => {
  //   const currentChatId = chatId; // ✅ 최신 chatId 가져오기
  //   const currentTopic = topic; // ✅ 최신 topic 가져오기
  //   const timestamp = new Date().toISOString(); // ✅ 현재 시간 기록
  
  //   const logData = {
  //     participantId: participantId,
  //     page: "Chat2_Survey",
  //     chatId: currentChatId, // ✅ 최신 chatId 반영
  //     topic: currentTopic, // ✅ 최신 topic 반영
  //     event: "Survey Submitted",
  //     responses: surveyResponses,
  //     timestamp: timestamp,
  //   };
  
  //   try {
  //     console.log(`[DEBUG] 로깅할 데이터:`, logData); // ✅ 실제 로그 데이터 확인
  
  //     // ✅ 설문 응답 로깅 요청
  //     await axios.post(`${BACKEND_URL}/log_survey`, logData);
  //     console.log(`[LOG] 설문 제출됨 - 시간: ${timestamp}, 응답:`, surveyResponses);
  //   } catch (error) {
  //     console.error("🚨 [ERROR] 설문 응답 로깅 실패:", error);
  //   }
  
  //   // ✅ 기존 설문 제출 처리
  //   setSurveyResponses({});
  //   setIsModalOpen(false);
  
  //   // ✅ 다음 페이지 이동
  //   if (parseInt(currentChatId) === 10) {
  //     navigate(`/pereval/epi?participantId=${participantId}`);
  //   } else {
  //     const nextChatId = parseInt(currentChatId) + 1;
  //     navigate(`/chat2/${nextChatId}?participantId=${participantId}`);
  //   }
  // };

  const handleSurveySubmit = async () => {
    const currentChatId = chatId;  // ✅ 최신 chatId 가져오기
    const currentTopic = topic;    // ✅ 최신 topic 가져오기
    const timestamp = new Date().toISOString();  // ✅ 현재 시간 기록

    const surveyData = {
        user_number: participantId,
        session_id: `chat2(epi)_${currentChatId}`, // ✅ chat1인지 chat2인지 명확히 구분
        topic: currentTopic, 
        responses: surveyResponses,
        timestamp: timestamp,
    };

    try {
        console.log(`[DEBUG] 설문 데이터 전송:`, surveyData);  // ✅ 실제 전송 데이터 확인

        // ✅ Firebase로 설문 데이터 저장 요청 (log_survey → submit_survey 변경!)
        await axios.post(`${BACKEND_URL}/submit_survey`, surveyData);
        console.log(`[LOG] 설문 제출됨 - 시간: ${timestamp}, 응답:`, surveyResponses);
    } catch (error) {
        console.error("🚨 [ERROR] 설문 제출 실패:", error);
    }

    // ✅ 기존 설문 제출 처리
    setSurveyResponses({});
    setIsModalOpen(false);

    // ✅ 다음 페이지 이동
    if (parseInt(currentChatId) === 10) {
        navigate(`/pereval/epi?participantId=${participantId}`);
    } else {
        const nextChatId = parseInt(currentChatId) + 1;
        navigate(`/chat2/${nextChatId}?participantId=${participantId}`);
    }
};
  


  // ✅ 설문 제출 핸들러
  // const submitSurvey = async () => {
  //   try {
  //     await axios.post("http://127.0.0.1:8000/submit_survey", {
  //       user_number: participantId,
  //       session_id: chatId,
  //       responses: surveyResponses,
  //     });

  //     alert("설문이 제출되었습니다.");
  //     setIsModalOpen(false);
  //   } catch (error) {
  //     console.error("🚨 [ERROR] 설문 제출 실패:", error);
  //   }
  // };

  useEffect(() => {
    const chatContainer = document.querySelector(".chat-messages");
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }, [messages]); // ✅ messages가 바뀔 때만 실행되도록 설정

    // ✅ 엔터 키 입력 이벤트 핸들러 추가
    const handleKeyPress = (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (!isSending) sendMessage(); // ✅ 전송 중이 아닐 때만 실행
      }
    };

    // ✅ 모달 열기/닫기 핸들러
  const handleOpenModal = () => {
    setSurveyResponses({});
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="page-container">
      <div className="fixed-shape">
      <span>Evaluating the Chat Experience with a Self-representative Persona >> Topic Selection >></span> 
        <p>&nbsp; Chat with Persona1 and Experience Evaluation</p> 
      </div>

      {/* ✅ 채팅 창 */}
      <div className="chat-container">
                        {/* ✅ 모달 컴포넌트 사용 */}
                        <Modal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          surveyQuestions={surveyQuestions}
          surveyResponses={surveyResponses}
          handleSurveyChange={handleSurveyChange}
          handleSurveySubmit={handleSurveySubmit}
        />

        <div className="chat-topic">
          <div className="topic-label">주제</div> 
          <div className="topic-connection">|</div> 
          <div className="topic-content">{topic}</div>
          <div className="topic-content">({chatId}/10)</div>
        </div>
        <hr className="chat-divider" />

        {/* ✅ 대화 메시지 표시 */}
        <div className="chat-messages">
          {messages.map((msg, index) => (
             <div key={index} className={msg.role === "user" ? "user-message-container" : "ai-message-container"}>
              {msg.role === "ai" && (
              <img 
                src="/profile.jpg" 
                // alt="AI 프로필" 
                className="ai-profile-image"
              />
            )}
          <div className={msg.role === "user" ? "user-message" : "ai-message"}>
              {msg.content}
            </div>
            </div>
          ))}

                {/* ✅ 하단 고정 메시지 입력창 */}
      <div className="messageBox">
        <textarea
          id="messageInput"
          value={inputText}
          onChange={(e) => {
            setInputText(e.target.value);
            e.target.style.height = "auto"; // ✅ 높이 초기화
            e.target.style.height = e.target.scrollHeight + "px"; // ✅ 내용에 맞춰 자동 확장
          }}
          onKeyDown={handleKeyPress}
          placeholder="메시지를 입력하세요..."
          rows={1} // ✅ 최소 한 줄 크기
        />


        {/* <input
          id="messageInput"
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyPress} 
          placeholder="메시지를 입력하세요..."
        /> */}

        <button id="sendButton" onClick={sendMessage}>
          <div className="svg-wrapper">
            <svg width="15" height="15" viewBox="0 0 24 24" stroke-width="1.5" stroke="white" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 12L22 2L14 22L10 14L2 12Z"></path>
            </svg>
          </div>
          <span>Enter</span>
        </button>

          {/* ✅ 대화 종료 버튼 추가 */}
          <button id="endButton" onClick={endConversation}>
          대화 종료
        </button>
      </div>
        </div>
      </div>



    {/* ✅ 모달 창 */}
    
    {/* {isModalOpen && (
        <div className="modal-container">
          <div className="modal-container-header">
            <h2 className="modal-container-title" style={{ color: "#ffffff" }}> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 대화 경험 평가 </h2>
            <button className="icon-button" onClick={handleCloseModal}>
            <svg width="20" height="20" viewBox="0 0 24 24" stroke-width="1.5" stroke="#000" fill="none" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
            </div>
          <div className="modal-container-body">
          {surveyQuestions.map((question, index) => (
              <div key={index} className="survey-question">
                <section className="experiment-procedure">
                <p style={{ color: "#ffffff",fontSize: "14.5px", fontWeight: "bold"}} >&nbsp;&nbsp;<strong>Q{index + 1}. {question}</strong></p> </section>
                <div className="scale-container">
                <span className="scale-label" >매우 <br/>그렇지 않다</span>
                  {[1, 2, 3, 4, 5, 6, 7].map((num) => (
                    <label key={num} className="scale-option">
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
                   <span className="scale-label">매우 <br/> 그렇다</span>
                </div>
                
              </div>
            ))}
          </div> */}




          <div className="modal-container-footer">
            {/* <button className="button is-ghost" onClick={handleCloseModal}>닫기</button> */}
            {/* <button className="button is-primary" onClick={handleSurveySubmit}>제출</button> */}
          </div>
        </div>
      )}

//     </div>
//   );
// };

export default Chat2;
