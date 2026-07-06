import sys
sys.path.append('modules')
from modules.semantic_analysis import compute_semantic_similarity

ans = "Newton's first law states that an object will keep moving or stay still unless some net force is applied to it."
ref = "Newton's first law of motion, also known as the law of inertia, states that an object at rest remains at rest, and an object in motion remains in motion with a constant velocity and in a straight line, unless acted upon by a net external force."

from modules.evaluation import evaluate_response

score = compute_semantic_similarity(ans, ref)
print("Paraphrased similarity score:", score)
res = evaluate_response(score, 0.0, 0, 0.15, 0.03, 10)
print("Paraphrased overall score:", res['overall_score'], "Category:", res['category'])

ans2 = "The birch canoes lid on the smooth planks."
score2 = compute_semantic_similarity(ans2, ref)
print("Completely different similarity score:", score2)
res2 = evaluate_response(score2, 0.0, 0, 0.15, 0.03, 10)
print("Completely different overall score:", res2['overall_score'], "Category:", res2['category'])

ans_photo = "Plants use photosynthesis to make food. They use sunlight, water, and carbon dioxide to make glucose and oxygen."
ref_photo = "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy. It requires carbon dioxide, water, and sunlight to produce glucose and oxygen, taking place in the chloroplasts using chlorophyll."
score_photo = compute_semantic_similarity(ans_photo, ref_photo)
print("Photosynthesis explanation similarity score:", score_photo)
res_photo = evaluate_response(score_photo, 0.0, 0, 0.15, 0.03, 10)
print("Photosynthesis overall score:", res_photo['overall_score'], "Category:", res_photo['category'])


