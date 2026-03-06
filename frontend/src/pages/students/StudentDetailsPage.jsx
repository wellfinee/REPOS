import { useParams } from "react-router-dom";

export default function StudentDetailsPage() {
  const { id } = useParams();
  return <h1>Student Details: {id}</h1>;
}
