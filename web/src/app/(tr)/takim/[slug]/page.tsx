import { TeamView, teamMetadata, teamParams } from "@/views/Team";

type Params = { params: Promise<{ slug: string }> };

export const generateStaticParams = teamParams;

export async function generateMetadata({ params }: Params) {
  return teamMetadata("tr", (await params).slug);
}

export default async function Page({ params }: Params) {
  return <TeamView lang="tr" slug={(await params).slug} />;
}
