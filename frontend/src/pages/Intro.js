import React, { useState } from "react";
import { useNavigate } from "react-router-dom";  
import axios from "axios";
import "./Intro.css";


const Intro = () => {
  const [name, setName] = useState("");
  const navigate = useNavigate(); 

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://multi-personas-backend.onrender.com"; 

  const handleStart = async () => {
    if (name.trim() === "") {
      alert("참가자 번호를 입력해주세요.");
      return;
    }

    const timestamp = new Date().toISOString(); // ✅ 현재 시간 저장

    try {
      console.log(`[INFO] 참가자 번호 요청: ${name}`);  // ✅ 요청 전 로그
      console.log(`[LOG] 시작 버튼 클릭됨 - 시간: ${timestamp}`);

            // ✅ 버튼 클릭 이벤트 로그 저장
            await axios.post(`${BACKEND_URL}/log_event`, {
              participantId: name,
              page: "Intro",
              button: "시작하기",
              timestamp: timestamp
            });

      const response = await axios.post(`${BACKEND_URL}/submit`, { participant_id: name });

      console.log("[INFO] 서버 응답:", response.data);  // ✅ FastAPI 응답 로그

      alert(`안녕하세요, ${name}님. 실험을 시작하겠습니다.`);

      // 1.5초 후 Info 페이지로 이동 (URL에 참가자 번호 포함)
      setTimeout(() => {
        // navigate(`/info?participantId=${name}`);
        navigate(`/topic?participantId=${name}`);  
      }, 1500);

    } catch (error) {
      console.error("[ERROR] 요청 실패:", error.response?.data || error.message);
      alert("서버 요청 중 오류가 발생했습니다.");
    }
  };


  return (
    <div className="intro-container">
      <header>
        <h1>자기 페르소나와 대화 경험 평가</h1>
      </header>
      
      <section className="researcher-intro">
        <p>안녕하세요. </p>
        <p>광주과학기술원 AI융합학과 Soft Computing & Interaction (SCI) 연구실 한민주 연구원입니다. </p>
        <p>저희 연구실에서 사용자와 가까운 페르소나와 상호작용에 대한 평가를 진행하고자 합니다.</p>
        <p>실험 참여자는 페르소나의 토대가 될 자신의 이야기를 입력하고, 채팅을 하게 됩니다.</p>
      </section>
      
      <section className="research-intro">
        <h2>연구 목적</h2>
        <p>본 연구는 사용자의 다중 정체성을 반영한 페르소나를 생성하고, 해당 페르소나를 내장한 에이전트와 대화 경험을 비교 및 평가하는 것에 목적을 두고 있습니다.</p>
        <img src="persona.png" alt="페르소나" className="process-image" />
      </section>

      <h2>페르소나란?</h2>
      <section className="experiment-procedure">
      <p>여러 정의가 있지만, 본 연구에서는 페르소나를 사용자 프로필로 정의합니다. 페르소나는 <strong>사용자의 정체성과 특성을 반영하는 명시적인 문장</strong>으로 구성됩니다.</p>
      <p>본 연구에서 페르소나는 에이전트에 사용자와 닮은 인격을 부여하기 위해 사용됩니다. 아래는 <strong>페르소나의 예</strong>입니다.</p>
      <p className="intro-text">내 이름은 홍길동이며, 25살입니다. 나의 취미는 영화 시청, 독서, 새로운 카페 방문하기 입니다. 일찍 일어나 계획적으로 하루를 끝내고 일기를 쓰는 것을 좋아합니다. 나는 가족, 친구, 여행, 대화를 좋아하고, 갈등, 스트레스, 정리정돈을 싫어합니다.</p>
      </section>
      <section className="experiment-procedure">
        <h2>실험 절차</h2>
        <p>본 실험은 <strong>사전 설문</strong> 후, 다음과 같이 진행됩니다.</p>
        <img src="process1.png" alt="실험 절차" className="process-image" />

          <li><strong>Step 1.</strong> 에이전트와 <strong>대화할 주제를 선택</strong>합니다. 25개의 선지 중 <strong>6개씩</strong>를 선택하게 됩니다. (2분)</li>
          <li><strong>Step 2.</strong> 첫번째 페르소나와 <strong>채팅 후, 대화 경험을 평가</strong>합니다. 채팅 및 평가가 <strong>10번</strong> 반복됩니다. (max. 35분)</li>
          <li><strong>Step 3.</strong> 첫번째 <strong>페르소나</strong>의 전반적인 <strong>품질을 평가</strong>합니다. (1분)</li>
          <li><strong>Step 4.</strong> 두번째 페르소나와 <strong>채팅 후, 대화 경험을 평가</strong>합니다. 채팅 및 평가가 <strong>10번</strong> 반복됩니다. (max. 35분)</li>
          <li><strong>Step 5.</strong> 두번째 <strong>페르소나</strong>의 전반적인 <strong>품질을 평가</strong>합니다. (1분)</li>
          <li><strong>Step 6.</strong> 마지막으로, 페르소나 생성에 사용된 <strong>정보를 평가</strong>합니다. (5분)</li>
          <li><strong>Step 7.</strong> <strong>사후 인터뷰를 진행</strong>합니다. (10분)</li>

        <h2>토픽 구성</h2>
        <p>대화할 토픽 분야는 아래와 같이 분류됩니다.</p>
        <li><strong>정보적 지원 토픽</strong>에서 에이전트는 일상적인 문제 해결 및 의사 결정을 돕기 위한 조언, 제안, 가이드를 제공합니다. 예) 주택 구매하기</li>
        <li><strong>정서적 지원 토픽</strong>에서 에이전트는 공감, 신뢰, 관심, 격려 등의 감정을 표현하고 제공하는 지원을 제공합니다. 예) 향수병 극복하기</li>
        <li><strong>평가적 지원 토픽</strong>에서 에이전트는 피드백, 사회적 비교, affirmation 등의 형태로 자기 평가를 수행할 수 있도록 돕습니다. 예) 시간 관리 평가받기</li>

        {/* <h2>자기 페르소나와 내면적 대화</h2>
        <p>대화적 자아 이론은 자아를 단일한 고정된 주체가 아니라, 다양한 "나-위치(I-positions)" 간의 상호작용으로 구성된 다성적 구조로 이해합니다.</p>
        <p>이러한 맥락에서, 자기 대화 및 내면 대화는 인간의 자기 인식, 감정 조절, 자기 통제, 자기 비판에 있어 핵심적인 심리적 메커니즘으로 작용합니다.</p>         
        <p>연구에 따르면, 1인칭이 아닌 3인칭(자신의 이름이나 he/she/they)으로 자신을 지칭하는 방식이 자기 거리두기를 유도하고,</p>
        <p>감정적으로 민감한 상황에서 더 적응적인 자기 성찰을 가능하게 합니다. </p>
        <p>자기 대화의 예로, 비행을 좋아하지 않는 제이슨이 비행 중에 긴장하거나 두려울 때 자신에게 말합니다.</p>
        <p className="intro-text">"글쎄, 나는 항공 여행이 매우 안전하다는 걸 알고 있어. 그리고 나는 전에 수천 번의 비행을 문제 없이 탔어."</p> */}

        <h2>페르소나 평가 요소</h2>
        <p>페르소나 평가는 아래 요소를 포함합니다. 해당 요소의 <strong>유무 혹은 정도</strong>를 생각하면서 채팅해 주시기 바랍니다.</p>
        <li><strong>자기 반영성:</strong> 해당 페르소나는 나의 성격이나 경험을 얼마나 잘 반영하는가? </li>
        <li><strong>자기 인식:</strong> 스스로를 이해하거나 객관적으로 보게 되는가? </li>
        <li><strong>자기 진실성:</strong> '보여지는 나'보다 '진실한 나'를 표현하게 되는가?</li>
        <li><strong>자기 성찰:</strong> 자신의 감정, 행동, 생각을 재고 혹은 회고하게 되는가? </li>
        <li><strong>자기 수용:</strong> 자신을 더 인정하거나 받아들이게 되는가?</li>
          

        <h2>시작하기</h2>
        <p>준비가 되셨으면, 아래의 빈칸에 <strong>참가자 번호</strong>를 적고 시작하기 버튼을 눌러주세요.</p>

        <div className="start-section">
        <div className="name-input-container">
          <input
            type="text"
            placeholder="예: P50"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="name-input"
          />
          <button onClick={handleStart} className="start-button">시작하기</button>
        </div>
        </div>
      </section>
    </div>
  );
};

export default Intro;