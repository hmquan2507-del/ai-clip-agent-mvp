import { redirect } from "next/navigation";

export default function UploadPage() {
  redirect("/workspace?intent=new");
}
