import {
	FileText,
	Lightbulb,
	ShieldAlert,
	BookOpen,
	Layers3,
	CheckCircle2,
	Hash,
} from "lucide-react";

function getText(value) {
	return typeof value === "string" ? value.trim() : "";
}


function SummarySection({ item, index }) {
  const section =
    getText(item?.concepto) ||
    getText(item?.seccion) ||
    getText(item?.titulo) ||
    getText(item?.title) ||
    `Sección ${index + 1}`;

  const description =
    getText(item?.impacto) ||
    getText(item?.contenido) ||
    getText(item?.descripcion) ||
    getText(item?.description) ||
    getText(item?.content);

  const recommendation =
    getText(item?.recomendacion) ||
    getText(item?.recommendation);

  const hint =
    getText(item?.pista_didactica) ||
    getText(item?.pista) ||
    getText(item?.hint);

  return (
    <article className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition duration-200 hover:border-blue-200 hover:shadow-md sm:p-6">
      <div className="flex items-start gap-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-700 transition group-hover:bg-blue-100">
          <Hash size={19} aria-hidden="true" />
        </div>

        <div className="min-w-0 flex-1">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-blue-700">
            Sección {String(index + 1).padStart(2, "0")}
          </p>

          <h3 className="text-base font-bold leading-snug text-slate-900 sm:text-lg">
            {section}
          </h3>

          {description && (
            <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-600">
              {description}
            </p>
          )}

          {recommendation && (
            <div className="mt-4 rounded-xl border border-blue-100 bg-blue-50 p-4">
              <h4 className="text-sm font-semibold text-blue-900">
                Recomendación
              </h4>
              <p className="mt-1 whitespace-pre-line text-sm leading-6 text-blue-800">
                {recommendation}
              </p>
            </div>
          )}

          {hint && (
            <div className="mt-5 flex items-start gap-3 rounded-xl bg-amber-50 p-4">
              <Lightbulb
                size={18}
                className="mt-0.5 shrink-0 text-amber-600"
                aria-hidden="true"
              />

              <div>
                <h4 className="text-sm font-semibold text-amber-900">
                  Pista didáctica
                </h4>
                <p className="mt-1 whitespace-pre-line text-sm leading-6 text-amber-800">
                  {hint}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}


function TextList({
	title,
	description,
	items,
	icon: Icon,
	variant = "default",
}) {
	if (!items.length) return null;

	const styles =
		variant === "warning"
			? {
					container: "border-amber-200 bg-amber-50/70",
					icon: "bg-amber-100 text-amber-700",
					item: "border-amber-200/80 bg-white",
					text: "text-amber-950",
					number: "bg-amber-100 text-amber-800",
				}
			: {
					container: "border-slate-200 bg-white",
					icon: "bg-blue-50 text-blue-700",
					item: "border-slate-200 bg-slate-50/70",
					text: "text-slate-700",
					number: "bg-blue-50 text-blue-700",
				};

	return (
		<section className={`rounded-2xl border p-5 sm:p-6 ${styles.container}`}>
			<div className='mb-5 flex items-center gap-3'>
				<div
					className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${styles.icon}`}>
					<Icon
						size={20}
						aria-hidden='true'
					/>
				</div>

				<div>
					<h3 className='font-bold text-slate-900'>{title}</h3>
					{description && (
						<p className='mt-0.5 text-sm text-slate-500'>{description}</p>
					)}
				</div>
			</div>

			<ul className='space-y-3'>
				{items.map((item, index) => (
					<li
						key={`${index}-${item}`}
						className={`flex items-start gap-3 rounded-xl border p-4 ${styles.item}`}>
						<span
							className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${styles.number}`}>
							{index + 1}
						</span>

						<p
							className={`min-w-0 flex-1 whitespace-pre-line text-sm leading-6 ${styles.text}`}>
							{item}
						</p>
					</li>
				))}
			</ul>
		</section>
	);
}

export function ExecutiveSummaryView({ content }) {
	const title =
		getText(content?.titulo) || getText(content?.title) || "Resumen ejecutivo";

	const introduction =
		getText(content?.introduccion_contextualizada) ||
		getText(content?.introduction) ||
		getText(content?.introduccion);

	const summary = getText(content?.summary) || getText(content?.resumen);

	// Esquema canónico del backend: content.items
	const rawItems = Array.isArray(content?.items) ? content.items : [];

	const sections = rawItems.filter(
		(item) =>
			item !== null && (typeof item === "object" || typeof item === "string"),
	);

	// Compatibilidad con la estructura anterior.
	const keyPoints = Array.isArray(content?.key_points)
		? content.key_points.filter(
				(point) => typeof point === "string" && point.trim(),
			)
		: [];

	const risks = Array.isArray(content?.risks)
		? content.risks.filter((risk) => typeof risk === "string" && risk.trim())
		: [];

	const hasContent = Boolean(
		introduction ||
		summary ||
		sections.length ||
		keyPoints.length ||
		risks.length,
	);

	if (!content || typeof content !== "object" || !hasContent) {
		return (
			<div
				role='status'
				className='rounded-2xl border border-slate-200 bg-white p-8 text-center'>
				<FileText
					className='mx-auto mb-3 text-slate-400'
					size={32}
					aria-hidden='true'
				/>

				<h3 className='font-semibold text-slate-800'>Resumen no disponible</h3>

				<p className='mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500'>
					No se recibió contenido para mostrar en este resumen ejecutivo.
				</p>
			</div>
		);
	}

	return (
		<section
			className='space-y-7'
			aria-label='Resumen ejecutivo'>
			{/* Portada del resumen */}
			<header className='relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-950 via-indigo-800 to-violet-600 p-6 text-white shadow-lg sm:p-8'>
				<div className='pointer-events-none absolute -right-10 -top-10 h-48 w-48 rounded-full bg-white/5' />
				<div className='pointer-events-none absolute -bottom-20 right-20 h-48 w-48 rounded-full bg-sky-300/10' />

				<div className='relative'>
					<div className='mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-blue-50'>
						<FileText
							size={15}
							aria-hidden='true'
						/>
						Resumen ejecutivo
					</div>

					<h2 className='max-w-3xl text-2xl font-bold leading-tight sm:text-3xl'>
						{title}
					</h2>

					{introduction && (
						<p className='mt-4 max-w-3xl whitespace-pre-line text-sm leading-7 text-blue-50 sm:text-base'>
							{introduction}
						</p>
					)}

					{sections.length > 0 && (
						<div className='mt-6 inline-flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm text-blue-50'>
							<Layers3
								size={16}
								aria-hidden='true'
							/>
							{sections.length}{" "}
							{sections.length === 1 ? "sección" : "secciones"}
						</div>
					)}
				</div>
			</header>

			{/* Síntesis general, si viene en un campo separado */}
			{summary && (
				<article className='rounded-2xl border border-blue-100 bg-blue-50/60 p-5 sm:p-6'>
					<div className='flex items-start gap-3'>
						<div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-700'>
							<BookOpen
								size={20}
								aria-hidden='true'
							/>
						</div>

						<div>
							<h3 className='font-bold text-slate-900'>Síntesis general</h3>
							<p className='mt-2 whitespace-pre-line text-sm leading-7 text-slate-700'>
								{summary}
							</p>
						</div>
					</div>
				</article>
			)}

			{/* Secciones reales del contenido */}
			{sections.length > 0 && (
				<div className='space-y-4'>
					<div className='flex items-center gap-3'>
						<div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-700'>
							<Layers3
								size={21}
								aria-hidden='true'
							/>
						</div>

						<div>
							<h3 className='text-lg font-bold text-slate-300'>
								Contenido principal
							</h3>
							<p className='text-sm text-slate-500'>
								Explora las ideas organizadas por sección.
							</p>
						</div>
					</div>

					<div className='space-y-4'>
						{sections.map((item, index) => {
							// También admite elementos que sean texto simple.
							const normalizedItem =
								typeof item === "string"
									? { seccion: `Idea ${index + 1}`, contenido: item }
									: item;

							return (
								<SummarySection
									key={`${index}-${normalizedItem.seccion ?? normalizedItem.titulo ?? ""}`}
									item={normalizedItem}
									index={index}
								/>
							);
						})}
					</div>
				</div>
			)}

			{/* Puntos clave: solo cuando existen en la respuesta */}
			<TextList
				title='Puntos clave'
				description='Ideas principales para recordar'
				items={keyPoints.map((point) => point.trim())}
				icon={Lightbulb}
			/>

			{/* Riesgos: no se infieren ni se inventan */}
			<TextList
				title='Riesgos identificados'
				description='Aspectos que requieren atención'
				items={risks.map((risk) => risk.trim())}
				icon={ShieldAlert}
				variant='warning'
			/>

			{/* Cierre visual cuando el resumen tiene secciones */}
			{sections.length > 0 && (
				<div className='flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-5'>
					<CheckCircle2
						size={21}
						className='mt-0.5 shrink-0 text-emerald-700'
						aria-hidden='true'
					/>

					<div>
						<h3 className='font-semibold text-emerald-950'>
							Resumen organizado
						</h3>
						<p className='mt-1 text-sm leading-6 text-emerald-800'>
							Has llegado al final de las secciones disponibles en esta
							adaptación. Consulta cada una para repasar sus ideas principales.
						</p>
					</div>
				</div>
			)}
		</section>
	);
}
