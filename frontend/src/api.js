export async function fetchUserCount() {
  const res = await fetch("http://192.168.0.75:8020/auth/user/count");
  return res.json();
}
