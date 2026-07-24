import { redirect } from "next/navigation";

export default function StylesPage() {
  redirect("/workspace?view=templates");
}
