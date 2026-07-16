import { SystemStatus } from "@/components/system-status";

const focusSkills = ["Front Lever", "Iron Cross"];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-surface px-6 py-8 text-ink">
      <section className="mx-auto flex w-full max-w-5xl flex-col gap-8">
        <header className="flex flex-col gap-3 border-b border-slate-200 pb-6">
          <p className="text-sm font-medium uppercase tracking-wide text-brand">
            Training Intelligence System
          </p>
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="max-w-2xl">
              <h1 className="text-3xl font-semibold tracking-normal md:text-5xl">
                Fundacao do projeto pronta para evoluir com dados reais.
              </h1>
              <p className="mt-4 max-w-xl text-base leading-7 text-slate-600">
                O objetivo inicial e registrar treinos de calistenia com contexto tecnico,
                percepcao de esforco, dor e historico comparavel.
              </p>
            </div>
            <SystemStatus />
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Foco inicial
            </h2>
            <ul className="mt-4 flex flex-col gap-2">
              {focusSkills.map((skill) => (
                <li key={skill} className="rounded-md bg-orange-50 px-3 py-2 text-sm text-orange-900">
                  {skill}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Backend
            </h2>
            <p className="mt-4 text-sm leading-6 text-slate-600">
              FastAPI, SQLAlchemy 2, Alembic, Pytest e PostgreSQL local via Docker Compose.
            </p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Frontend
            </h2>
            <p className="mt-4 text-sm leading-6 text-slate-600">
              Next.js, TypeScript, Tailwind CSS, React Hook Form, Zod, TanStack Query e Recharts.
            </p>
          </div>
        </section>
      </section>
    </main>
  );
}

