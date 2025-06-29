const admin = require("firebase-admin");

/**
 * 🔹 Firestore Timestamp 변환 함수
 */
function convertTimestamp(timestamp) {
    if (timestamp && timestamp._seconds !== undefined) {
        return new Date(timestamp._seconds * 1000).toISOString();
    }
    return timestamp;
}

/**
 * 🔹 문서 데이터 + 서브컬렉션까지 가져오는 함수 (재귀 호출)
 */
async function getDocumentWithSubcollections(docRef) {
    const docSnapshot = await docRef.get();
    let docData = docSnapshot.data() || {}; // ✅ 문서 데이터 가져오기

    // 🔹 Firestore Timestamp 변환
    for (const key in docData) {
        docData[key] = convertTimestamp(docData[key]);
    }

    // 🔹 서브컬렉션 조회 및 데이터 저장
    const subcollections = await docRef.listCollections();
    for (const subcollection of subcollections) {
        const subcollectionSnapshot = await subcollection.get();
        const subcollectionData = {};

        subcollectionSnapshot.forEach(doc => {
            let data = doc.data();
            for (const key in data) {
                data[key] = convertTimestamp(data[key]);
            }
            subcollectionData[doc.id] = data; // ✅ 서브컬렉션 내부 문서 데이터 추가
        });

        docData[subcollection.id] = subcollectionData; // ✅ 서브컬렉션 추가
    }

    return docData;
}

module.exports = { convertTimestamp, getDocumentWithSubcollections };
