const admin = require("firebase-admin");
const fs = require("fs");
const { getDocumentWithSubcollections } = require("./utils");

// 🔹 Firebase Admin SDK 초기화
const serviceAccount = require("/Users/hanminju/LangChat/frontend/src/serviceAccountKey_.json");

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

/**
 * 🔹 Firestore 컬렉션 내보내기 (서브컬렉션 포함)
 */
async function exportCollection(collectionName, fileName) {
    const collectionData = {};

    try {
        console.log(`📡 [INFO] '${collectionName}' 컬렉션 데이터 가져오는 중...`);
        const collectionSnapshot = await db.collection(collectionName).listDocuments();

        for (const docRef of collectionSnapshot) {
            collectionData[docRef.id] = await getDocumentWithSubcollections(docRef);
        }

        if (!fs.existsSync("firestore")) {
            fs.mkdirSync("firestore", { recursive: true });
        }

        // 🔹 JSON 파일로 저장
        fs.writeFileSync(`firestore/${fileName}`, JSON.stringify(collectionData, null, 2));

        console.log(`✅ '${collectionName}' 데이터를 firestore/${fileName} 파일로 저장 완료!`);
    } catch (error) {
        console.error(`🚨 [ERROR] '${collectionName}' 데이터 가져오기 실패:`, error);
    }
}

/**
 * 🔹 Firestore 전체 데이터 내보내기 실행
 */
async function exportAllFirestore() {
    await exportCollection("Eval_logs", "Eval_logs.json"); // ✅ Eval_logs 저장
    await exportCollection("Eval_logs(chat)", "Eval_chat.json"); // ✅ Eval_logs(chat) 저장
    await exportCollection("button_logs", "button_logs.json"); // ✅ button_logs 저장
    await exportCollection("chat_logs", "chat_logs.json"); // ✅ chat_logs 저장
    await exportCollection("user_topics", "user_topics.json"); // ✅ user_topics 저장
}

// ✅ 실행
exportAllFirestore();
