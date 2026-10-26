import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { ArrowLeft, Download, RefreshCw, Trash2 } from "lucide-react";

import { GenerationStatus } from "@/widgets/generation-status/GenerationStatus";
import { ContentViewer } from "@/widgets/content-viewer/ContentViewer";
import { adaptationsApi } from "@/shared/api";

import { Card } from "@/shared/ui/Card";
import { Badge } from "@/shared/ui/Badge";
import { Button } from "@/shared/ui/Button";
import { Alert } from "@/shared/ui/Alert";

import { ADAPTATION_POLL_POLICY } from "./adaptationPolling";

// ── Polling helpers ────────────────────────────────────────────────────────────

function isTerminalStatus(status) {
	return status === "completed" || status === "failed";
}

function useAdaptationResult(id, initialAdaptation) {
	const [adaptation, setAdaptation] = useState(initialAdaptation);
	const [loading, setLoading] = useState(!initialAdaptation);
	const [error, setError] = useState(null);
	const [pollRun, setPollRun] = useState(0);

	useEffect(() => {
		let active = true;
		let timeoutId;
		let activeStatusController;
		let attempts = 0;

		const loadFullAdaptation = async () => {
			const fullAdaptation = await adaptationsApi.get(id);

			if (active) {
				setAdaptation(fullAdaptation);
			}

			return fullAdaptation;
		};

		const scheduleNextPoll = () => {
			timeoutId = setTimeout(pollStatus, ADAPTATION_POLL_POLICY.intervalMs);
		};

		const pollStatus = async () => {
			if (!active) return;

			const controller = new AbortController();

			activeStatusController = controller;
			attempts += 1;

			try {
				const statusUpdate = await adaptationsApi.getStatus(id, {
					signal: controller.signal,
				});

				if (!active) return;

				setError(null);

				setAdaptation((prev) => ({
					...prev,
					...statusUpdate,
				}));

				if (isTerminalStatus(statusUpdate.status)) {
					await loadFullAdaptation();
					return;
				}

				if (attempts >= ADAPTATION_POLL_POLICY.maxAttempts) {
					setError(
						"Se agotó el tiempo de espera para completar la adaptación. " +
							"Reintenta la consulta o vuelve al historial.",
					);
					return;
				}

				scheduleNextPoll();
			} catch (err) {
				if (active && err.name !== "AbortError") {
					setError(
						err.message ?? "Error al consultar el estado de la adaptación.",
					);
				}
			} finally {
				if (activeStatusController === controller) {
					activeStatusController = undefined;
				}

				if (active) {
					setLoading(false);
				}
			}
		};

		if (initialAdaptation && !isTerminalStatus(initialAdaptation.status)) {
			if (pollRun > 0) {
				pollStatus();
			} else {
				scheduleNextPoll();
			}
		} else {
			loadFullAdaptation()
				.then((fullAdaptation) => {
					if (active && !isTerminalStatus(fullAdaptation.status)) {
						scheduleNextPoll();
					}

					if (active) {
						setError(null);
					}
				})
				.catch((err) => {
					if (active) {
						setError(err.message ?? "Error al cargar la adaptación.");
					}
				})
				.finally(() => {
					if (active) {
						setLoading(false);
					}
				});
		}

		return () => {
			active = false;

			clearTimeout(timeoutId);
			activeStatusController?.abort();
		};
	}, [id, initialAdaptation, pollRun]);

	// Reinicia el ciclo de consulta del estado.
	const retryPolling = () => {
		setError(null);
		setLoading(true);
		setPollRun((currentRun) => currentRun + 1);
	};

	return {
		adaptation,
		loading,
		error,
		retryPolling,
	};
}

// ── Sub-components ────────────────────────────────────────────────────────────

function AdaptationMeta({ adaptation }) {
	return (
		<div>
			<h1 className='page-title'>{adaptation.documentTitle ?? "Resultado"}</h1>

			<div className='flex flex-wrap items-center gap-2 mt-2'>
				{adaptation.profile && (
					<Badge variant='brand'>{adaptation.profile}</Badge>
				)}

				{adaptation.format && (
					<Badge variant='violet'>{adaptation.format}</Badge>
				)}

				{adaptation.industry && (
					<Badge variant='default'>{adaptation.industry}</Badge>
				)}

				{adaptation.detailLevel && (
					<Badge variant='default'>{adaptation.detailLevel}</Badge>
				)}
			</div>
		</div>
	);
}

/**
 * Guía para revisar el recurso generado y contrastarlo
 * con el documento original.
 */
function ReviewGuide({ adaptation }) {
	const [checkedItems, setCheckedItems] = useState({});

	const reviewItems = [
		{
			id: "concepts",
			title: "Verificar los conceptos principales",
			description:
				"Comprueba que las ideas importantes se expliquen correctamente.",
		},
		{
			id: "facts",
			title: "Comprobar datos y afirmaciones",
			description:
				"Revisa nombres, fechas, cifras y afirmaciones importantes en la fuente.",
		},
		{
			id: "omissions",
			title: "Identificar omisiones o información dudosa",
			description:
				"Busca información relevante que falte, resulte ambigua o no esté respaldada.",
		},
		{
			id: "source",
			title: "Contrastar con el documento original",
			description:
				"Abre el documento original desde la opción de consulta o descarga disponible en NuevaMente y compara los puntos clave.",
		},
	];

	const completedCount = reviewItems.filter(
		(item) => checkedItems[item.id],
	).length;

	const configuration = [
		{ label: "Perfil", value: adaptation.profile },
		{ label: "Formato", value: adaptation.format },
		{ label: "Sector", value: adaptation.industry },
		{ label: "Nivel de detalle", value: adaptation.detailLevel },
	].filter(
		(item) =>
			item.value !== null &&
			item.value !== undefined &&
			String(item.value).trim() !== "",
	);

	return (
		<Card>
			<div className='space-y-6'>
				<div>
					<h2 className='text-lg font-semibold text-slate-100'>
						Revisa tu recurso antes de utilizarlo
					</h2>
					<p className='mt-1 text-sm text-slate-300'>
						Comprueba que el contenido adaptado sea claro, útil y coherente con
						el documento original.
					</p>
				</div>

				{configuration.length > 0 && (
					<section aria-labelledby='review-configuration-title'>
						<h3
							id='review-configuration-title'
							className='mb-3 text-sm font-semibold text-slate-200'>
							Configuración utilizada
						</h3>

						<div className='flex flex-wrap gap-2'>
							{configuration.map((item) => (
								<div
									key={item.label}
									className='rounded-lg border border-slate-200 bg-slate-50 px-3 py-2'>
									<p className='text-xs text-slate-500'>{item.label}</p>
									<p className='text-sm font-medium text-slate-800'>
										{item.value}
									</p>
								</div>
							))}
						</div>
					</section>
				)}

				<section aria-labelledby='review-checklist-title'>
					<div className='mb-3 flex flex-wrap items-center justify-between gap-2'>
						<h3
							id='review-checklist-title'
							className='text-sm font-semibold text-slate-200'>
							Lista de comprobación
						</h3>

						<Badge variant='default'>
							{completedCount} de {reviewItems.length}
						</Badge>
					</div>

					<div className='space-y-3'>
						{reviewItems.map((item) => (
							<label
								key={item.id}
								className='flex cursor-pointer items-start gap-3 rounded-lg border border-slate-200 p-3 transition-colors hover:bg-slate-50'>
								<input
									type='checkbox'
									checked={Boolean(checkedItems[item.id])}
									onChange={(event) =>
										setCheckedItems((previous) => ({
											...previous,
											[item.id]: event.target.checked,
										}))
									}
									className='mt-1 h-4 w-4 shrink-0 accent-green-600'
								/>

								<span className='min-w-0'>
									<span className='block text-sm font-medium text-slate-100'>
										{item.title}
									</span>
									<span className='mt-1 block text-sm text-slate-300'>
										{item.description}
									</span>
								</span>
							</label>
						))}
					</div>
				</section>

				<div
					role='note'
					className='rounded-lg border border-amber-200 bg-amber-50 p-4'>
					<p className='text-sm font-semibold text-amber-900'>
						Importante: revisa antes de compartir
					</p>
					<p className='mt-1 text-sm text-amber-800'>
						La adaptación automática puede contener errores, omisiones o
						interpretaciones inexactas. Una puntuación de similitud de
						fragmentos, si está disponible, no garantiza la exactitud del
						contenido. Contrasta siempre la información importante con el
						documento original.
					</p>
				</div>
			</div>
		</Card>
	);
}

function PageHeader({ adaptation, onExport, exporting, onDelete, deleting }) {
	return (
		<div className='flex flex-wrap items-center justify-between gap-3'>
			<Link
				to='/'
				className='btn-ghost text-sm flex  text-slate-200 items-center gap-1.5'>
				<ArrowLeft className='w-4 h-4' />
				Volver al inicio
			</Link>

			{adaptation.status === "completed" && (
				<div className='flex flex-wrap gap-2'>
					<Button
						variant='secondary'
						size='sm'
						onClick={onExport}
						disabled={exporting || deleting}
						leftIcon={<Download className='w-4 h-4' />}>
						{exporting ? "Exportando..." : "Exportar PDF"}
					</Button>

					<Button
						variant='danger'
						size='sm'
						onClick={onDelete}
						disabled={deleting || exporting}

						leftIcon={<Trash2 className='w-4 h-4'/>}>
						{deleting ? "Eliminando..." : "Eliminar"}
					</Button>
				</div>
			)}
		</div>
	);
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function ResultPage() {
	const { id } = useParams();
	const { state } = useLocation();

	const { adaptation, loading, error, retryPolling } = useAdaptationResult(
		id,
		state?.adaptation ?? null,
	);

	// Estado de exportación del PDF.
	const [exporting, setExporting] = useState(false);
	const [exportError, setExportError] = useState(null);
	const [exportSuccess, setExportSuccess] = useState(false);

	// Borrado adaptación

	const [deleting, setDeleting] = useState(false);
	const [deleteError, setDeleteError] = useState(null);

	const handleDelete = async () => {
		const confirmed = window.confirm(
			"¿Estás seguro de que deseas eliminar esta adaptación? Esta acción no se puede deshacer.",
		);

		if (!confirmed) return;

		setDeleting(true);
		setDeleteError(null);

		try {
			await adaptationsApi.delete(adaptation.id);
			window.location.assign("/history?deleted=success");
		} catch (err) {
			setDeleteError(err?.message ?? "No se pudo eliminar la adaptación.");
		} finally {
			setDeleting(false);
		}
	};

	// Genera y descarga el PDF de la adaptación.
	const handleExport = async () => {
		setExportError(null);
		setExportSuccess(false);
		setExporting(true);

		try {
			const { exportAdaptationPdf } = await import("./exportAdaptationPdf");

			await exportAdaptationPdf(adaptation);
			setExportSuccess(true);
		} catch (err) {
			setExportError(
				err?.message ?? "No se pudo generar el PDF. Inténtalo nuevamente.",
			);
		} finally {
			setExporting(false);
		}
	};

	// Estado inicial de carga.
	if (loading && !adaptation) {
		return (
			<div className='max-w-3xl mx-auto'>
				<Card>
					<div className='flex items-center gap-3'>
						<RefreshCw className='w-5 h-5 animate-spin text-blue-600' />

						<p className='text-sm text-slate-500'>Cargando adaptación...</p>
					</div>
				</Card>
			</div>
		);
	}

	// Adaptación inexistente o no disponible.
	if (!adaptation) {
		return (
			<div className='max-w-3xl mx-auto'>
				<Alert
					variant='error'
					title='Adaptación no encontrada'>
					<p>
						{error ?? "No se pudo cargar la información de esta adaptación."}
					</p>

					<Link
						to='/history'
						className='block mt-3 text-sm underline'>
						Ver historial
					</Link>
				</Alert>
			</div>
		);
	}

	const isProcessing =
		adaptation.status === "processing" || adaptation.status === "pending";

	return (
		<div className='max-w-4xl mx-auto space-y-8 animate-fade-in'>
			{/* Encabezado y exportación */}
			<PageHeader
				adaptation={adaptation}
				onExport={handleExport}
				exporting={exporting}
				onDelete={handleDelete}
				deleting={deleting}
			/>

			{/* Mensaje de error de borrado */}
			{deleteError && (
				<Alert
					variant='error'
					title='No se pudo eliminar la adaptación'>
					<p>{deleteError}</p>
				</Alert>
			)}

			{/* Información general de la adaptación */}
			<AdaptationMeta adaptation={adaptation} />

			{/* Mensaje de error de exportación */}
			{exportError && (
				<Alert
					variant='error'
					title='No se pudo exportar el PDF'>
					<p>{exportError}</p>

					<div className='mt-3'>
						<Button
							variant='secondary'
							size='sm'
							onClick={handleExport}
							disabled={exporting}>
							Intentar nuevamente
						</Button>
					</div>
				</Alert>
			)}

			{/* Mensaje de exportación completada */}
			{exportSuccess && (
				<Alert title='PDF generado'>
					<p>
						Se solicitó la descarga de tu material de estudio. Si no aparece,
						revisa las descargas del navegador.
					</p>
				</Alert>
			)}

			{/* Error al consultar el estado de generación */}
			{error && (
				<Alert
					variant='error'
					title='No se pudo actualizar el estado'>
					<p>{error}</p>

					<div className='mt-3 flex flex-wrap gap-2'>
						<Button
							variant='secondary'
							size='sm'
							onClick={retryPolling}>
							Reintentar consulta
						</Button>

						<Link
							to='/history'
							className='btn-ghost text-sm'>
							Ver historial
						</Link>
					</div>
				</Alert>
			)}

			{/* Estado del procesamiento */}
			{isProcessing && (
				<Card>
					<GenerationStatus status={adaptation.status} />
				</Card>
			)}

			{/* Contenido generado */}
			{adaptation.status === "completed" && (
				<>
					<ContentViewer adaptation={adaptation} />

					{/* Guía de revisión del recurso */}
					<ReviewGuide adaptation={adaptation} />
				</>
			)}

			{/* Error durante la generación */}
			{adaptation.status === "failed" && (
				<Alert
					variant='error'
					title='Error en la generación'>
					<p>
						{adaptation.error ?? "Ocurrió un error durante el procesamiento."}
					</p>

					<div className='mt-3 flex flex-wrap gap-2'>
						<Link to='/new'>
							<Button
								variant='secondary'
								size='sm'
								leftIcon={<RefreshCw className='w-4 h-4' />}>
								Intentar nuevamente
							</Button>
						</Link>

						<Link
							to='/history'
							className='btn-ghost text-sm'>
							Ver historial
						</Link>
					</div>
				</Alert>
			)}

			{/* Acciones posteriores al resultado */}
			{adaptation.status === "completed" && (
				<div className='flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-5'>
					<Link
						to='/history'
						className='btn-ghost text-sm'>
						Ver historial de adaptaciones
					</Link>

					<Link to='/new'>
						<Button
							variant='primary'
							size='sm'>
							Crear otra adaptación
						</Button>
					</Link>
				</div>
			)}
		</div>
	);
}
