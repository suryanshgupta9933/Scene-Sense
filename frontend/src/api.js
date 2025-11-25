export async function fetchUserCount() {
  const res = await fetch("http://localhost:8000/auth/user/count");
  return res.json();
}
