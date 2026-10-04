import { useState } from "react";
import {
	BookOpen,
	HelpCircle,
	AlignLeft,
	Presentation,
	FileCheck,
	Clock,
	CheckCircle2,
	Cloud,
	ChevronLeft,
	ChevronRight,
	Sparkles,
} from "lucide-react";

import { Badge } from "@/shared/ui/Badge";
import { Card } from "@/shared/ui/Card";
import { ScoreRing } from "@/shared/ui/Alert";
import { cn } from "@/shared/utils";
import { FlashCard } from "@/widgets/flash-card/FlashCard";
import { adaptFlashcardsResponse } from "./adaptFlashcardsResponse";

// ── Format icon map ───────────────────────────────────────────────────────────

const FORMAT_ICONS = {
	Flashcards: HelpCircle,
	Tutorial: BookOpen,
	"Resumen Ejecutivo": FileCheck,
	Quiz: AlignLeft,
	Guion: Presentation,
};

// ── Format-specific views ─────────────────────────────────────────────────────

/**
 * Vista real de Flashcards.
 *
 * Esta implementación reemplaza la antigua FlashcardsPage.
 * Consume directamente la adaptación generada por el backend.
 */
function FlashcardsView({ result }) {
	const [currentIndex, setCurrentIndex] = useState(0);

	if (result.status === "invalid") {
		return (
			<div role='alert' className='p-8 text-center text-rose-300'>
				La respuesta recibida no cumple el contrato de flashcards.
			</div>
		);
	}

	if (result.status === "empty") {
		return (
			<div role='status' className='p-8 text-center text-slate-400'>
				No hay flashcards para mostrar.
			</div>
		);
	}

	const {
		title,
		introduction,
		profile,
		studyTime,
		keyConcepts,
		qualityScore,
		remarks,
		bucket,
		objectId,
		items,
	} = result.viewModel;

	const handleNext = () => {
		if (currentIndex < items.length - 1) {
			setCurrentIndex((prev) => prev + 1);
		}
	};

	const handlePrev = () => {
		if (currentIndex > 0) {
			setCurrentIndex((prev) => prev - 1);
		}
	};

	return (
		<div className='min-h-screen bg-slate-950 text-slate-100 py-10 px-4 sm:px-6 lg:px-8'>
			<div className='max-w-4xl mx-auto space-y-8'>
				{/* HEADER AND PEDAGOGICAL METADATA */}
				<div className='bg-slate-900/80 rounded-2xl p-6 sm:p-8 shadow-md border border-slate-800'>
					<div className='flex flex-wrap items-center justify-between gap-4 mb-4'>
						{/* Profile */}
						<span className='inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-900/40 text-indigo-300 border border-indigo-800/50'>
							<Sparkles className='w-3.5 h-3.5' />
							Perfil Objetivo: {profile}
						</span>

						{/* Study metadata */}
						<div className='flex items-center gap-4 text-xs font-medium text-slate-400'>
							<span className='flex items-center gap-1'>
								<Clock className='w-4 h-4 text-slate-500' />~{studyTime} min
								tiempo de estudio
							</span>

							<span className='flex items-center gap-1 text-emerald-400 bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-900/50'>
								<CheckCircle2 className='w-4 h-4' />
								Anclaje RAG: {(qualityScore * 100).toFixed(0)}%
							</span>
						</div>
					</div>

					{/* Title */}
					<h2 className='text-2xl sm:text-3xl font-bold text-slate-50 mb-2'>
						{title}
					</h2>

					{/* Introduction */}
					<p className='text-slate-400 text-sm sm:text-base leading-relaxed mb-6'>
						{introduction}
					</p>

					{/* KEY CONCEPTS */}
					{keyConcepts.length > 0 && (
						<div className='border-t border-slate-800/80 pt-4 flex flex-wrap items-center gap-2'>
							<span className='text-xs font-semibold text-slate-400 flex items-center gap-1 mr-2'>
								<BookOpen className='w-3.5 h-3.5' />
								Conceptos clave:
							</span>

							{keyConcepts.map((concept, index) => (
								<span
									key={index}
									className='px-2.5 py-1 bg-slate-800 text-slate-300 rounded-md text-xs font-medium border border-slate-700'>
									{concept}
								</span>
							))}
						</div>
					)}
				</div>

				{/* FLASHCARD VIEWER */}
				<div>
					<FlashCard
						key={currentIndex}
						item={items[currentIndex]}
						index={currentIndex}
						total={items.length}
					/>

					{/* NAVIGATION CONTROLS */}
					<div className='flex items-center justify-between max-w-xl mx-auto mt-4 px-2'>
						<button
							type='button'
							onClick={handlePrev}
							disabled={currentIndex === 0}
							className='flex items-center gap-1 px-4 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm font-semibold text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed shadow-sm transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-400'>
							<ChevronLeft className='w-4 h-4' />
							Anterior
						</button>

						<span className='text-sm font-medium text-slate-400'>
							{currentIndex + 1} / {items.length}
						</span>

						<button
							type='button'
							onClick={handleNext}
							disabled={currentIndex === items.length - 1}
							className='flex items-center gap-1 px-4 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed shadow-sm transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-400'>
							Siguiente
							<ChevronRight className='w-4 h-4' />
						</button>
					</div>
				</div>

				{/* FOOTER: OCI OBJECT STORAGE STATUS & REMARKS */}
				{(bucket || objectId || remarks) && (
					<div className='bg-slate-900/50 rounded-xl p-4 flex flex-wrap justify-between items-center text-xs text-slate-400 gap-2 border border-slate-800'>
						{(bucket || objectId) && (
							<div className='flex items-center gap-2'>
								<Cloud className='w-4 h-4 text-slate-500' />

								<span>
									Persistido en <strong>Bucket OCI:</strong>{" "}
									{bucket || "No disponible"}
									{" | ID: "}
									<code className='bg-slate-800 px-1.5 py-0.5 rounded text-slate-300 border border-slate-700'>
										{objectId || "No disponible"}
									</code>
								</span>
							</div>
						)}

						{remarks && (
							<span className='italic text-slate-500'>{remarks}</span>
						)}
					</div>
				)}
			</div>
		</div>
	);
}

function TutorialView({ content }) {
	return (
		<div className='space-y-6'>
			{content.introduction && (
				<div className='p-4 bg-brand-600/10 border border-brand-600/20 rounded-xl'>
					<p className='text-sm font-semibold text-brand-300 mb-2'>
						Introducción
					</p>

					<p className='text-sm text-slate-300'>{content.introduction}</p>
				</div>
			)}

			{content.steps?.map((step, i) => (
				<div
					key={i}
					className='flex gap-4'>
					<div className='flex-shrink-0 w-8 h-8 rounded-full bg-brand-600/20 border border-brand-600/30 flex items-center justify-center text-brand-400 font-bold text-sm'>
						{i + 1}
					</div>

					<div className='flex-1'>
						<p className='font-semibold text-slate-200 text-sm'>{step.title}</p>

						<p className='text-sm text-slate-400 mt-1'>{step.content}</p>

						{step.example && (
							<pre className='mt-2 p-3 bg-slate-900 rounded-lg text-xs text-slate-300 overflow-x-auto'>
								{step.example}
							</pre>
						)}
					</div>
				</div>
			))}

			{content.conclusion && (
				<div className='p-4 bg-emerald-600/10 border border-emerald-600/20 rounded-xl'>
					<p className='text-sm font-semibold text-emerald-300 mb-2'>
						Conclusión
					</p>

					<p className='text-sm text-slate-300'>{content.conclusion}</p>
				</div>
			)}
		</div>
	);
}

function ExecutiveSummaryView({ content }) {
	return (
		<div className='space-y-5'>
			{content.summary && (
				<div>
					<p className='text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2'>
						Resumen
					</p>

					<p className='text-slate-300 text-sm leading-relaxed'>
						{content.summary}
					</p>
				</div>
			)}

			{content.key_points?.length > 0 && (
				<div>
					<p className='text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2'>
						Puntos Clave
					</p>

					<ul className='space-y-2'>
						{content.key_points.map((point, i) => (
							<li
								key={i}
								className='flex items-start gap-2 text-sm text-slate-300'>
								<span className='w-1.5 h-1.5 rounded-full bg-brand-400 mt-1.5 flex-shrink-0' />
								{point}
							</li>
						))}
					</ul>
				</div>
			)}

			{content.risks?.length > 0 && (
				<div>
					<p className='text-xs font-semibold uppercase tracking-wider text-amber-500 mb-2'>
						Riesgos
					</p>

					<ul className='space-y-2'>
						{content.risks.map((risk, i) => (
							<li
								key={i}
								className='flex items-start gap-2 text-sm text-amber-300'>
								<span className='w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0' />
								{risk}
							</li>
						))}
					</ul>
				</div>
			)}
		</div>
	);
}

function QuizView({ content }) {
	return (
		<div className='space-y-6'>
			{content.questions?.map((q, i) => (
				<div
					key={i}
					className='p-5 bg-slate-800 rounded-xl border border-slate-700'>
					<div className='flex items-start justify-between gap-2 mb-3'>
						<p className='text-sm font-semibold text-slate-200'>
							{i + 1}. {q.question}
						</p>

						<Badge
							variant='default'
							size='sm'>
							{q.difficulty}
						</Badge>
					</div>

					<div className='space-y-2'>
						{q.options?.map((opt, j) => (
							<div
								key={j}
								className={cn(
									"flex items-center gap-3 p-3 rounded-lg text-sm border transition-colors",
									opt === q.correct_answer
										? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
										: "bg-slate-700/40 border-slate-700 text-slate-400",
								)}>
								<span className='font-medium'>
									{String.fromCharCode(65 + j)}.
								</span>

								{opt}
							</div>
						))}
					</div>

					{q.justification && (
						<p className='text-xs text-slate-500 mt-3 pt-3 border-t border-slate-700'>
							💡 {q.justification}
						</p>
					)}
				</div>
			))}
		</div>
	);
}

/**
 * Guion view — structured display will be implemented once the schema is finalised.
 * Currently renders a formatted JSON fallback.
 */
function GuionView({ content }) {
	return (
		<pre className='text-sm text-slate-300 whitespace-pre-wrap bg-slate-900 p-5 rounded-xl overflow-x-auto'>
			{JSON.stringify(content, null, 2)}
		</pre>
	);
}

function formatLabel(key) {
	return key.replace(/_/g, " ");
}

function CanonicalValue({ value }) {
	if (Array.isArray(value)) {
		return (
			<ul className='space-y-1'>
				{value.map((item, i) => (
					<li key={i}>
						{typeof item === "object" ? JSON.stringify(item) : item}
					</li>
				))}
			</ul>
		);
	}

	if (value && typeof value === "object") {
		return (
			<pre className='text-xs text-slate-300 whitespace-pre-wrap bg-slate-900/70 p-3 rounded-lg overflow-x-auto'>
				{JSON.stringify(value, null, 2)}
			</pre>
		);
	}

	return <span>{value}</span>;
}

function CanonicalContentView({ content }) {
	const items = Array.isArray(content.items) ? content.items : [];

	return (
		<div className='space-y-5'>
			{content.titulo && (
				<div>
					<p className='text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2'>
						Título
					</p>

					<p className='text-slate-100 font-semibold'>{content.titulo}</p>
				</div>
			)}

			{content.introduccion_contextualizada && (
				<div className='p-4 bg-brand-600/10 border border-brand-600/20 rounded-xl'>
					<p className='text-sm font-semibold text-brand-300 mb-2'>
						Introducción
					</p>

					<p className='text-sm text-slate-300'>
						{content.introduccion_contextualizada}
					</p>
				</div>
			)}

			{items.length > 0 && (
				<div className='space-y-3'>
					<p className='text-xs font-semibold uppercase tracking-wider text-slate-500'>
						Elementos generados
					</p>

					{items.map((item, i) => (
						<div
							key={i}
							className='p-5 bg-slate-800 rounded-xl border border-slate-700 space-y-3'>
							<Badge
								variant='default'
								size='sm'>
								Elemento {i + 1}
							</Badge>

							{Object.entries(item).map(([key, value]) => (
								<div key={key}>
									<p className='text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1'>
										{formatLabel(key)}
									</p>

									<div className='text-sm text-slate-300'>
										<CanonicalValue value={value} />
									</div>
								</div>
							))}
						</div>
					))}
				</div>
			)}
		</div>
	);
}

// ── Format renderer map ───────────────────────────────────────────────────────

const FORMAT_VIEWS = {
	Tutorial: TutorialView,
	"Resumen Ejecutivo": ExecutiveSummaryView,
	Quiz: QuizView,
	Guion: GuionView,
};

// ── Evaluation breakdown ──────────────────────────────────────────────────────

function EvaluationBreakdown({ evaluation }) {
	if (!evaluation?.criteria) return null;

	return (
		<Card>
			<p className='text-sm font-semibold text-slate-300 mb-4'>
				Evaluación del Critic Agent
			</p>

			<div className='grid grid-cols-2 sm:grid-cols-4 gap-4'>
				{Object.entries(evaluation.criteria).map(([key, val]) => (
					<div
						key={key}
						className='text-center'>
						<p className='text-lg font-bold text-slate-100'>
							{Math.round(val * 100)}%
						</p>

						<p className='text-xs text-slate-500 mt-0.5 capitalize'>
							{key.replace(/_/g, " ")}
						</p>
					</div>
				))}
			</div>
		</Card>
	);
}

// ── Main component ────────────────────────────────────────────────────────────

/**
 * Renders the generated educational content based on the adaptation format.
 *
 * Flashcards use their dedicated interactive view.
 * Other formats preserve the existing rendering behavior.
 *
 * @param {Object} props
 * @param {import('@/shared/types').Adaptation} props.adaptation
 */
export function ContentViewer({ adaptation }) {
	if (!adaptation || adaptation.status !== "completed") {
		return null;
	}
	const flashcardsResult =
		adaptation.format === "Flashcards"
			? adaptFlashcardsResponse(adaptation)
			: null;
	if (!adaptation.content && !flashcardsResult) return null;

	const FormatIcon = FORMAT_ICONS[adaptation.format] ?? BookOpen;

	const FormatView = FORMAT_VIEWS[adaptation.format];

	const { evaluation } = adaptation;
	const content = adaptation.content ?? {};

	const usesCanonicalBackendContent = Boolean(
		content.titulo ||
		content.introduccion_contextualizada ||
		Array.isArray(content.items),
	);

	return (
			<div className='space-y-6'>
			{/* Header */}
			<div className='flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 bg-slate-800/60 rounded-xl border border-slate-700/50'>
				<div className='flex items-center gap-3'>
					<div className='w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center'>
						<FormatIcon className='w-5 h-5 text-white' />
					</div>

					<div>
						<p className='font-semibold text-slate-100'>{adaptation.format}</p>

						<div className='flex items-center gap-2 mt-0.5'>
							<Badge
								variant='brand'
								size='sm'>
								{adaptation.profile}
							</Badge>

							<Badge
								variant='default'
								size='sm'>
								{adaptation.industry}
							</Badge>
						</div>
					</div>
				</div>

				{evaluation && (
					<div className='flex items-center gap-4'>
						<div className='text-right'>
							<p className='text-xs text-slate-500'>Calidad Critic</p>

							<p className='text-xs text-slate-400 mt-0.5'>
								{evaluation.approved ? "✅ Aprobado" : "❌ No aprobado"}
							</p>
						</div>

						<ScoreRing
							score={evaluation.score}
							size={64}
						/>
					</div>
				)}
			</div>

			{/* Format-specific content */}

			{adaptation.format === "Flashcards" ? (
				<FlashcardsView result={flashcardsResult} />
			) : usesCanonicalBackendContent ? (
				<CanonicalContentView content={content} />
			) : FormatView ? (
				<FormatView content={content} />
			) : (
				<pre className='text-sm text-slate-300 whitespace-pre-wrap bg-slate-900 p-5 rounded-xl'>
					{JSON.stringify(content, null, 2)}
				</pre>
			)}

			<EvaluationBreakdown evaluation={evaluation} />
		</div>
	);
}
