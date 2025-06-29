import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios"; 
import Tooltip from "../components/Tooltip";
import "./Info.css";

const Info = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // URL에서 participantId 추출
  const queryParams = new URLSearchParams(location.search);
  const participantId = queryParams.get("participantId") || "Unknown";

  // 콘솔에서 참가자 번호 확인
  useEffect(() => {
    console.log(`[INFO] 참가자 번호 확인: ${participantId}`);
  }, [participantId]);

  const [baseInfo, setBaseInfo] = useState({
    나이: "",
    성별: "",
    직업: "",
    전공: "",
    MBTI: "",
  });

  const [selfTags, setSelfTags] = useState(["", "", "", "", "", ""]);
  const [roles, setRoles] = useState([
    { role: "", episodes: ["", ""] },
    { role: "", episodes: ["", ""] },
    { role: "", episodes: ["", ""] },
  ]);

  const handleBaseChange = (e) => {
    const { name, value } = e.target;
    setBaseInfo((prev) => ({ ...prev, [name]: value }));
  };

  const handleTagChange = (index, value) => {
    const updatedTags = [...selfTags];
    updatedTags[index] = value;
    setSelfTags(updatedTags);
  };

  const handleRoleChange = (index, value) => {
    const updatedRoles = [...roles];
    updatedRoles[index].role = value;
    setRoles(updatedRoles);
  };

  const handleEpisodeChange = (roleIndex, episodeIndex, value) => {
    const updatedRoles = [...roles];
    updatedRoles[roleIndex].episodes[episodeIndex] = value;
    setRoles(updatedRoles);
  };

  // 📝 백엔드로 사용자 정보 전송하는 함수
  const handleSubmit = async () => {  // ✅ async 추가
    const userData = {
      Age: baseInfo.나이,
      Gender: baseInfo.성별,
      Job: baseInfo.직업,
      Major: baseInfo.전공,
      MBTI: baseInfo.MBTI,
      Self_tag: selfTags.join(", "),
      Episode: {
        "Role 1": {
          Role: roles[0].role,
          Ep1: roles[0].episodes[0],
          Ep2: roles[0].episodes[1],
        },
        "Role 2": {
          Role: roles[1].role,
          Ep1: roles[1].episodes[0],
          Ep2: roles[1].episodes[1],
        },
        "Role 3": {
          Role: roles[2].role,
          Ep1: roles[2].episodes[0],
          Ep2: roles[2].episodes[1],
        }
      }
    };

    try {
      console.log("📡 [INFO] 서버로 데이터 전송 중...", userData);

      // ✅ FastAPI 서버로 사용자 데이터 전송
      const response = await axios.post(`http://127.0.0.1:8000/save_user_info/${participantId}`, userData);

      console.log("✅ [SUCCESS] 파일 저장 완료:", response.data);
      alert("제출되었습니다!");

      navigate(`/topic?participantId=${participantId}`);

    } catch (error) {
      console.error("🚨 [ERROR] 파일 저장 실패:", error);
      alert("파일 저장 중 오류가 발생했습니다.");
    }
};

  const HorizonLine = ({ text }) => {
    return (
      <div
        style={{
          fontFamily: 'NanumSquareNeo',
          width: "95%",
          textAlign: "center",
          borderBottom: "1px solid #aaa",
          lineHeight: "0.15em",
          margin: "10px auto"
        }}
      >
        <span style={{ background: "#aaa", 
                      padding: "0 20px", 
                      color: "#ffffff" ,
                      fontSize: "1.0em"
                    }}>{text}</span>
      </div>
    );
  };



  return (
      <div className="page-container">
      <div className="fixed-shape">
    <span>자기 페르소나와 대화 경험 평가 >> </span> <p>&nbsp; 정보 입력</p> {/* 아이콘 또는 텍스트 추가 가능 */}
  </div>

      
      <div className="info-container">
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>자신을 반영하는 페르소나를 만들기 위해서 활용될 정보를 입력해주세요.</p>

      <section className="base-info">
        <h2>기본 정보</h2>
        <div className="grid-container">
        {Object.keys(baseInfo).map((key) => (
          <input
            key={key}
            type="text"
            name={key}
            placeholder={key}
            value={baseInfo[key]}
            onChange={handleBaseChange}
          />
        ))}
        </div>
      </section>

      <section className="self-tags">
        <h2>성격 태그</h2>
        
        <section className="experiment-procedure">
        <p>자신을 잘 설명하는 <strong>자기 정의적 성격 태그</strong> 6가지를 작성해주세요.</p>
        <p><strong>예를 들어,</strong> 아래와 같은 성격 태그가 있을 수 있습니다. <strong>자유롭게 입력</strong>해주세요.</p>
        </section>

        <p></p>
        {/* 태그 예제 추가 */}
        <div className="tag-container">
        {["쾌활함", "성실함", "유머스러움", "차분함", "비판적", "낙관적", "감정적", "강박적", "etc"].map((tag, index) => (
          <span key={index} className="tag">{tag}</span>
        ))}
         </div>
        <p></p>

        <div className="grid-container">
        {selfTags.map((tag, index) => (
          <input
            key={index}
            type="text"
            placeholder={`성격 태그 ${index + 1}`}
            value={tag}
            onChange={(e) => handleTagChange(index, e.target.value)}
          />
        ))}
        </div>
      </section>

      <section className="narrative">
        <h2>역할 & 에피소드</h2>
        <section className="experiment-procedure">
        <p> 정체성 형성에 가장 큰 영향을 주었던, 혹은 주고있는 <strong>역할</strong> 및 <strong>관련된 경험/에피소드/이야기</strong>를 작성해주세요. 이러한 정보는 실험자의 다중정체성을 반영할 수 있습니다.</p>
        <p><strong>예를 들어,</strong> 아래와 같은 역할 및 에피소드가 있을 수 있습니다. <strong>자유롭게 작성</strong>해주세요.</p>
        </section>
        
        <p> </p>
        <p> </p>
        <div className="example-container">
        <div className = "example-title">공상가</div>
        <HorizonLine text="Ep 1" />
        <div className = "example-text">나는 어려서부터 상상하기를 좋아했다. 초등학교 때는 수업 중 다른 생각을 하다가 갑자기 웃음을 터트려 친구들로부터 이상한 시선을 받은 적도 있었다. 또, 친구들과 언쟁하거나 토론하는 상황에서 이렇게 흘러갔다면 어땠을까? 하는 생각도 자주 한다. 친구들은 가끔 넌 진짜 편견이 없다고 말해주곤 한다. 한가지 상황으로도 여러가지 방향으로 상상의 나래를 펼쳐보며 생각이 보다 유연해진 것 같다.</div>
        <HorizonLine text="Ep 2" />
        <div className = "example-text">공상과 상상은 나의 중요한 원동력이다. 일명 ‘행복회로’를 돌리면서 내가 원하는 미래를 상상하고, 지금의 행동이 그 미래로 나를 이끌 수 있다는 것을 자각할 때 나는 어떤 행동을 할 힘이 생긴다.</div>
        </div>
        <div className="example-container">
        <div className = "example-title">시골 출생자</div>
        <HorizonLine text="Ep 1" />
        <div className = "example-text">나는 무안이라는 작은 시골 마을에서 나고 자랐다. 무안은 친구들도, 지인들도 한 다리를 건너면 다 알 만큼 작은 도시다. 외향적이고 새로운 것을 좋아하는 나에게 무안은 사랑하는 고향인 동시에 답답한 공간이었다.</div>
        <HorizonLine text="Ep 2" />
        <div className = "example-text">시간이 많이 지나고 처음으로 친구들과 외국의 대도시로 여행을 떠났다. 부모님으로부터 자유로웠고 모두 내 용돈과 내 선택으로 이루어졌다. 그 여행이 너무 설렜기 때문에 나는 큰 도시로 떠나는 것, 여행하는 것을 사랑하게 되었다. 외향적이고 생기 넘치는 분위기를 좋아하던 내가 도시 여행의 기쁨을 남들보다 유난히 더 크게 느끼는 것은 이런 이유라고 생각한다.</div>
        </div>

        {roles.map((role, roleIndex) => (
          <div key={roleIndex} className="role-section">
            <input
              type="text"
              placeholder={`Role ${roleIndex + 1}`}
              value={role.role}
              onChange={(e) => handleRoleChange(roleIndex, e.target.value)}
            />
            {role.episodes.map((episode, episodeIndex) => (
              <textarea
                key={episodeIndex}
                placeholder={`Episode ${episodeIndex + 1}`}
                value={episode}
                onChange={(e) => handleEpisodeChange(roleIndex, episodeIndex, e.target.value)}
              />
            ))}
          </div>
        ))}
      </section>

      <button onClick={handleSubmit} className="submit-button">제출하기</button>
    </div>
    </div>
  );
};

export default Info;