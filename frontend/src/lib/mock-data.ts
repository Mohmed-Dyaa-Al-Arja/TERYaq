import type { ChatAnswer, Conversation } from "./types";

/**
 * Mock data used while no backend is configured (VITE_API_BASE_URL unset).
 * Delete this file once the real API is connected.
 */
export function mockAnswer(question: string): ChatAnswer {
  return {
    answer:
      "Breast cancer screening can provide important benefits through early detection, but it is also associated with several potential harms. The primary harms include false-positive results — where the screening test indicates cancer when none is present — leading to unnecessary additional imaging, biopsies, and significant psychological distress. Overdiagnosis, the detection of cancers that would not have caused harm during a patient's lifetime, is considered the most significant long-term harm. Additional harms include a small radiation-induced cancer risk from repeated mammography and procedural complications from biopsies prompted by false-positive recalls.",
    evidence_status: "Strong",
    evidence_grounded: true,
    source_traceable: true,
    reference_backed: true,
    evidence_match: 87,
    retrieved_count: 4,
    passed_threshold_count: 3,
    next_step: "Consult a qualified healthcare professional for personal medical decisions.",
    follow_up_questions: [
      "What are the proven benefits of breast cancer screening?",
      "How do false-positive rates vary by age and breast density?",
      "What is the recommended screening interval for average-risk women?",
    ],
    citations: [
      {
        id: "WHO-BC-2023-001",
        title: "WHO Position Paper on Breast Cancer Screening",
        source: "WHO",
        page: 24,
        chunk_id: "WHO-BC-2023-001-CH-0042",
        section: "Balance of benefits and harms",
        year: 2023,
        score: 0.89,
        used_in_answer: true,
        passage:
          "Screening programmes must weigh mortality reduction against harms such as false positives, overdiagnosis and overtreatment. Programme quality assurance is essential to keep recall rates within accepted limits.",
      },
      {
        id: "IARC-HANDB-2016",
        title: "IARC Handbooks of Cancer Prevention: Breast Cancer Screening",
        source: "IARC",
        page: 117,
        chunk_id: "IARC-HANDB-2016-CH-0188",
        section: "Harms of mammography screening",
        year: 2016,
        score: 0.81,
        used_in_answer: true,
        passage:
          "The main harms of mammography screening include false-positive recall rates, overdiagnosis, radiation exposure, and anxiety related to the screening process. False-positive rates vary by age, breast density, and screening interval.",
      },
      {
        id: "USPSTF-BC-2024",
        title: "USPSTF Recommendation Statement: Breast Cancer Screening",
        source: "USPSTF",
        page: 8,
        chunk_id: "USPSTF-BC-2024-CH-0019",
        section: "Potential harms",
        year: 2024,
        score: 0.76,
        used_in_answer: true,
        passage:
          "Harms of screening include false-positive results leading to additional imaging and biopsies, overdiagnosis and overtreatment, and radiation exposure from repeated mammography.",
      },
    ],
  };
}

const now = Date.now();

export const mockConversations: Conversation[] = [
  {
    id: "seed-1",
    title: "What are the potential harms associated with breast cancer screening?",
    createdAt: now - 1000 * 60 * 19,
    updatedAt: now - 1000 * 60 * 19,
    messages: [
      {
        id: "seed-1-u",
        role: "user",
        content: "What are the potential harms associated with breast cancer screening?",
        createdAt: now - 1000 * 60 * 19,
      },
      {
        id: "seed-1-a",
        role: "assistant",
        content: "",
        createdAt: now - 1000 * 60 * 19,
        answer: mockAnswer("harms"),
      },
    ],
  },
  {
    id: "seed-2",
    title: "What are the recommended intervals for mammography screening in women aged 40-49?",
    createdAt: now - 1000 * 60 * 60 * 5,
    updatedAt: now - 1000 * 60 * 60 * 5,
    messages: [
      {
        id: "seed-2-u",
        role: "user",
        content:
          "What are the recommended intervals for mammography screening in women aged 40-49?",
        createdAt: now - 1000 * 60 * 60 * 5,
      },
      {
        id: "seed-2-a",
        role: "assistant",
        content: "",
        createdAt: now - 1000 * 60 * 60 * 5,
        answer: {
          ...mockAnswer("intervals"),
          answer:
            "Recommendations vary by organization. The USPSTF recommends biennial screening for women aged 40-49, while the American Cancer Society recommends offering annual screening from age 40 with a shared decision-making discussion about benefits and harms.",
          evidence_match: 82,
        },
      },
    ],
  },
  {
    id: "seed-3",
    title: "How effective is ultrasound as a supplemental screening tool for dense breast tissue?",
    createdAt: now - 1000 * 60 * 60 * 8,
    updatedAt: now - 1000 * 60 * 60 * 8,
    messages: [
      {
        id: "seed-3-u",
        role: "user",
        content:
          "How effective is ultrasound as a supplemental screening tool for dense breast tissue?",
        createdAt: now - 1000 * 60 * 60 * 8,
      },
      {
        id: "seed-3-a",
        role: "assistant",
        content: "",
        createdAt: now - 1000 * 60 * 60 * 8,
        answer: {
          ...mockAnswer("ultrasound"),
          answer:
            "Supplemental ultrasound screening in women with dense breasts can detect additional cancers not visualised on mammography, though it is associated with higher false-positive rates and additional biopsies.",
          evidence_status: "Moderate",
          evidence_match: 64,
        },
      },
    ],
  },
];
