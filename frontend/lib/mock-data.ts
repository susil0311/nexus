import type {
  Project, DashboardData, ScheduleActivity, ReviewItem,
  ForecastData, Anomaly, MemoryResponse
} from './api'

// ─── Mock Projects ────────────────────────────────────────────────────────────
export const mockProjects: Project[] = [
  {
    id: 'proj-001',
    name: 'Kaziranga Natural Gas Pipeline',
    client: 'Assam Gas Company Ltd.',
    location: 'Kaziranga, Assam, India',
    lat: 26.5775,
    lng: 93.1711,
    start_date: '2024-01-15',
    planned_finish: '2025-06-30',
    status: 'active',
    spi: 0.87,
    cpi: 0.92,
    progress: 54,
    disciplines: ['Civil', 'Piping', 'Electrical', 'Instrumentation', 'Mechanical'],
  },
  {
    id: 'proj-002',
    name: 'Brahmaputra River Crossing',
    client: 'ONGC Ltd.',
    location: 'Dibrugarh, Assam, India',
    lat: 27.4728,
    lng: 94.9120,
    start_date: '2024-06-01',
    planned_finish: '2025-12-31',
    status: 'active',
    spi: 0.95,
    cpi: 0.97,
    progress: 28,
    disciplines: ['Civil', 'Piping', 'Mechanical'],
  },
]

// ─── Mock Dashboard ───────────────────────────────────────────────────────────
export const mockDashboard: DashboardData = {
  spi: 0.87,
  cpi: 0.92,
  spi_trend: -0.03,
  cpi_trend: 0.01,
  total_activities: 248,
  completed_activities: 134,
  at_risk_count: 22,
  delayed_count: 8,
  not_started_count: 36,
  recent_submissions: [
    { id: 's1', description: 'Pipeline welding reach 3A completed — 45m', status: 'done', discipline: 'Piping', submitted_by: 'Rajesh Kumar', submitted_at: new Date(Date.now() - 1800000).toISOString(), matched_activity: 'PIP-WLD-003A', confidence: 0.94 },
    { id: 's2', description: 'Concrete pouring for valve station VS-04 foundation', status: 'processing', discipline: 'Civil', submitted_by: 'Amlan Barua', submitted_at: new Date(Date.now() - 3600000).toISOString() },
    { id: 's3', description: 'Cable tray installation complete at CP-12', status: 'done', discipline: 'Electrical', submitted_by: 'Priya Nath', submitted_at: new Date(Date.now() - 7200000).toISOString(), matched_activity: 'ELE-CTR-012', confidence: 0.89 },
    { id: 's4', description: 'ROW clearing blocked at km 23 due to encroachment issue', status: 'failed', discipline: 'Civil', submitted_by: 'Biren Das', submitted_at: new Date(Date.now() - 10800000).toISOString() },
    { id: 's5', description: 'Hydro test for reach 2B passed successfully — 100 bar', status: 'done', discipline: 'Piping', submitted_by: 'Dipak Gogoi', submitted_at: new Date(Date.now() - 14400000).toISOString(), matched_activity: 'PIP-HYD-002B', confidence: 0.97 },
    { id: 's6', description: 'Soil compaction test results pending lab', status: 'pending', discipline: 'Civil', submitted_by: 'Manas Boruah', submitted_at: new Date(Date.now() - 18000000).toISOString() },
  ],
  discipline_breakdown: [
    { discipline: 'Civil', total: 78, completed: 42, at_risk: 8, delayed: 3 },
    { discipline: 'Piping', total: 96, completed: 51, at_risk: 7, delayed: 4 },
    { discipline: 'Electrical', total: 42, completed: 24, at_risk: 4, delayed: 1 },
    { discipline: 'Instrumentation', total: 18, completed: 10, at_risk: 2, delayed: 0 },
    { discipline: 'Mechanical', total: 14, completed: 7, at_risk: 1, delayed: 0 },
  ],
  scurve_data: [
    { date: '2024-01-15', planned: 0, actual: 0 },
    { date: '2024-02-01', planned: 2, actual: 1.8 },
    { date: '2024-03-01', planned: 6, actual: 5.2 },
    { date: '2024-04-01', planned: 12, actual: 10.5 },
    { date: '2024-05-01', planned: 20, actual: 17.8 },
    { date: '2024-06-01', planned: 29, actual: 25.4 },
    { date: '2024-07-01', planned: 38, actual: 32.1 },
    { date: '2024-08-01', planned: 47, actual: 40.2 },
    { date: '2024-09-01', planned: 54, actual: 47.0 },
    { date: '2024-10-01', planned: 62, actual: null as unknown as number },
    { date: '2024-11-01', planned: 70, actual: null as unknown as number },
    { date: '2024-12-01', planned: 80, actual: null as unknown as number },
    { date: '2025-01-01', planned: 88, actual: null as unknown as number },
    { date: '2025-03-01', planned: 95, actual: null as unknown as number },
    { date: '2025-06-30', planned: 100, actual: null as unknown as number },
  ],
}

// ─── Mock Schedule ────────────────────────────────────────────────────────────
export const mockSchedule: ScheduleActivity[] = [
  {
    id: 'a1', wbs_code: '1', name: 'Kaziranga Gas Pipeline Project', discipline: 'All',
    planned_start: '2024-01-15', planned_finish: '2025-06-30', progress: 54,
    float_days: 0, status: 'at_risk', level: 0,
    children: [
      {
        id: 'a2', wbs_code: '1.1', name: 'Civil Works', discipline: 'Civil',
        planned_start: '2024-01-15', planned_finish: '2025-03-31', progress: 56,
        float_days: 5, status: 'on_track', level: 1,
        children: [
          { id: 'a3', wbs_code: '1.1.1', name: 'ROW Clearing & Grading', discipline: 'Civil', planned_start: '2024-01-15', planned_finish: '2024-04-30', actual_start: '2024-01-18', actual_finish: '2024-05-12', progress: 100, float_days: 0, status: 'completed', level: 2 },
          { id: 'a4', wbs_code: '1.1.2', name: 'Trench Excavation Reach 1-4', discipline: 'Civil', planned_start: '2024-03-01', planned_finish: '2024-09-30', actual_start: '2024-03-10', progress: 72, float_days: 8, status: 'on_track', level: 2 },
          { id: 'a5', wbs_code: '1.1.3', name: 'Valve Station VS-04 Foundation', discipline: 'Civil', planned_start: '2024-06-01', planned_finish: '2024-08-31', actual_start: '2024-06-15', progress: 45, float_days: -3, status: 'delayed', level: 2 },
          { id: 'a6', wbs_code: '1.1.4', name: 'Backfilling & Compaction', discipline: 'Civil', planned_start: '2024-08-01', planned_finish: '2025-02-28', progress: 28, float_days: 12, status: 'on_track', level: 2 },
        ],
      },
      {
        id: 'a7', wbs_code: '1.2', name: 'Piping & Pipeline', discipline: 'Piping',
        planned_start: '2024-02-01', planned_finish: '2025-05-31', progress: 53,
        float_days: -2, status: 'at_risk', level: 1,
        children: [
          { id: 'a8', wbs_code: '1.2.1', name: 'Pipe Stringing Reach 1-2', discipline: 'Piping', planned_start: '2024-02-01', planned_finish: '2024-06-30', actual_start: '2024-02-05', actual_finish: '2024-07-08', progress: 100, float_days: 0, status: 'completed', level: 2 },
          { id: 'a9', wbs_code: '1.2.2', name: 'Welding Reach 3A-3B', discipline: 'Piping', planned_start: '2024-05-01', planned_finish: '2024-10-31', actual_start: '2024-05-12', progress: 68, float_days: -5, status: 'at_risk', level: 2 },
          { id: 'a10', wbs_code: '1.2.3', name: 'Welding Reach 4A-4B', discipline: 'Piping', planned_start: '2024-08-01', planned_finish: '2025-02-28', progress: 22, float_days: 6, status: 'on_track', level: 2 },
          { id: 'a11', wbs_code: '1.2.4', name: 'Hydrostatic Testing', discipline: 'Piping', planned_start: '2024-10-01', planned_finish: '2025-04-30', progress: 15, float_days: 0, status: 'not_started', level: 2 },
        ],
      },
      {
        id: 'a12', wbs_code: '1.3', name: 'Electrical Systems', discipline: 'Electrical',
        planned_start: '2024-04-01', planned_finish: '2025-04-30', progress: 57,
        float_days: 10, status: 'on_track', level: 1,
        children: [
          { id: 'a13', wbs_code: '1.3.1', name: 'Cable Tray Installation', discipline: 'Electrical', planned_start: '2024-04-01', planned_finish: '2024-09-30', actual_start: '2024-04-08', progress: 78, float_days: 14, status: 'on_track', level: 2 },
          { id: 'a14', wbs_code: '1.3.2', name: 'MV Cabling CP Stations', discipline: 'Electrical', planned_start: '2024-07-01', planned_finish: '2025-01-31', progress: 34, float_days: 7, status: 'on_track', level: 2 },
          { id: 'a15', wbs_code: '1.3.3', name: 'Substation Equipment Install', discipline: 'Electrical', planned_start: '2024-09-01', planned_finish: '2025-03-31', progress: 8, float_days: 3, status: 'at_risk', level: 2 },
        ],
      },
      {
        id: 'a16', wbs_code: '1.4', name: 'Instrumentation & Control', discipline: 'Instrumentation',
        planned_start: '2024-06-01', planned_finish: '2025-05-31', progress: 41,
        float_days: 15, status: 'on_track', level: 1,
        children: [
          { id: 'a17', wbs_code: '1.4.1', name: 'SCADA Panel Installation', discipline: 'Instrumentation', planned_start: '2024-06-01', planned_finish: '2024-11-30', progress: 60, float_days: 18, status: 'on_track', level: 2 },
          { id: 'a18', wbs_code: '1.4.2', name: 'Field Instrument Commissioning', discipline: 'Instrumentation', planned_start: '2024-10-01', planned_finish: '2025-04-30', progress: 12, float_days: 10, status: 'not_started', level: 2 },
        ],
      },
      {
        id: 'a19', wbs_code: '1.5', name: 'Mechanical Equipment', discipline: 'Mechanical',
        planned_start: '2024-05-01', planned_finish: '2025-04-30', progress: 50,
        float_days: 20, status: 'on_track', level: 1,
        children: [
          { id: 'a20', wbs_code: '1.5.1', name: 'Compressor Station Equipment', discipline: 'Mechanical', planned_start: '2024-05-01', planned_finish: '2025-02-28', progress: 50, float_days: 20, status: 'on_track', level: 2 },
        ],
      },
    ],
  },
]

// ─── Mock Review Queue ────────────────────────────────────────────────────────
export const mockReviewQueue: ReviewItem[] = [
  {
    id: 'r1',
    submission_id: 's-001',
    extracted_text: 'Completed hydro test on reach 3B pipeline section — pressure held at 100 bar for 24 hours, no leaks detected',
    extracted_date: '2024-09-03',
    discipline: 'Piping',
    status: 'pending',
    created_at: new Date(Date.now() - 3600000).toISOString(),
    candidates: [
      { activity_id: 'a11', activity_name: 'Hydrostatic Testing', wbs_code: '1.2.4', score: 0.94, explanation: 'High semantic match on "hydro test" + "reach" + pressure testing context. Date aligns with planned activity window.', discipline: 'Piping' },
      { activity_id: 'a9', activity_name: 'Welding Reach 3A-3B', wbs_code: '1.2.2', score: 0.61, explanation: 'Partial match on "reach 3B" but hydro test implies post-weld QA, not welding activity itself.', discipline: 'Piping' },
      { activity_id: 'a8', activity_name: 'Pipe Stringing Reach 1-2', wbs_code: '1.2.1', score: 0.23, explanation: 'Low match — pipeline section reference but different reach and activity type.', discipline: 'Piping' },
    ],
  },
  {
    id: 'r2',
    submission_id: 's-002',
    extracted_text: 'Cable tray installation finished at Compressor Station CP-12, 85 meters completed today',
    extracted_date: '2024-09-04',
    discipline: 'Electrical',
    status: 'pending',
    created_at: new Date(Date.now() - 7200000).toISOString(),
    candidates: [
      { activity_id: 'a13', activity_name: 'Cable Tray Installation', wbs_code: '1.3.1', score: 0.97, explanation: 'Exact semantic match on "cable tray installation". CP-12 location confirmed in activity scope documentation.', discipline: 'Electrical' },
      { activity_id: 'a14', activity_name: 'MV Cabling CP Stations', wbs_code: '1.3.2', score: 0.54, explanation: 'Moderate match — CP station reference, but cabling vs tray installation are distinct activities.', discipline: 'Electrical' },
      { activity_id: 'a15', activity_name: 'Substation Equipment Install', wbs_code: '1.3.3', score: 0.18, explanation: 'Low match — different activity type; equipment installation vs cable management.', discipline: 'Electrical' },
    ],
  },
  {
    id: 'r3',
    submission_id: 's-003',
    extracted_text: 'Excavation work stalled at chainage 14+500 due to unexpected rock formation, blasting permit required',
    extracted_date: '2024-09-04',
    discipline: 'Civil',
    status: 'pending',
    created_at: new Date(Date.now() - 10800000).toISOString(),
    candidates: [
      { activity_id: 'a4', activity_name: 'Trench Excavation Reach 1-4', wbs_code: '1.1.2', score: 0.88, explanation: 'Strong match on excavation + chainage reference. Chainage 14+500 falls within Reach 2 of the pipeline corridor.', discipline: 'Civil' },
      { activity_id: 'a3', activity_name: 'ROW Clearing & Grading', wbs_code: '1.1.1', score: 0.41, explanation: 'Partial — ROW work co-located but grading precedes excavation in sequence.', discipline: 'Civil' },
      { activity_id: 'a6', activity_name: 'Backfilling & Compaction', wbs_code: '1.1.4', score: 0.12, explanation: 'Very low match — wrong activity phase; backfilling is post-pipe installation.', discipline: 'Civil' },
    ],
  },
  {
    id: 'r4',
    submission_id: 's-004',
    extracted_text: 'SCADA panel FAT (factory acceptance test) conducted at vendor facility Bangalore, all 48 I/O channels verified',
    extracted_date: '2024-09-02',
    discipline: 'Instrumentation',
    status: 'pending',
    created_at: new Date(Date.now() - 18000000).toISOString(),
    candidates: [
      { activity_id: 'a17', activity_name: 'SCADA Panel Installation', wbs_code: '1.4.1', score: 0.76, explanation: 'Good match on SCADA panel — FAT is a pre-installation milestone that gates this activity. I/O count aligns with design spec.', discipline: 'Instrumentation' },
      { activity_id: 'a18', activity_name: 'Field Instrument Commissioning', wbs_code: '1.4.2', score: 0.45, explanation: 'Partial — I/O verification relates to commissioning but FAT specifically applies to panel installation phase.', discipline: 'Instrumentation' },
      { activity_id: 'a16', activity_name: 'Instrumentation & Control (WBS)', wbs_code: '1.4', score: 0.29, explanation: 'Parent WBS level match — but submission should map to specific activity.', discipline: 'Instrumentation' },
    ],
  },
]

// ─── Mock Forecast ────────────────────────────────────────────────────────────
export const mockForecast: ForecastData = {
  predicted_finish: '2025-09-15',
  planned_finish: '2025-06-30',
  delay_days: 77,
  confidence: 0.82,
  risk_factors: [
    { name: 'Monsoon Season Impact', impact_percent: 38, description: 'Historical productivity data shows 35-45% productivity reduction during June-September monsoon in Assam region.' },
    { name: 'ROW Encroachment Delays', impact_percent: 29, description: 'Land access disputes at km 22-25 causing recurring stoppage of trenching activities.' },
    { name: 'Rock Formation Blasting', impact_percent: 21, description: 'Unexpected hard rock at chainage 14+500 requires blasting permits — average 6 week approval cycle.' },
    { name: 'Material Supply Chain', impact_percent: 12, description: 'Pipe delivery delays from Jindal Steel — 3 batches running 2-3 weeks behind schedule.' },
  ],
  scurve_forecast: [
    { date: '2024-01-15', planned: 0, actual: 0, optimistic: 0, pessimistic: 0 },
    { date: '2024-03-01', planned: 6, actual: 5.2, optimistic: 5.2, pessimistic: 5.2 },
    { date: '2024-05-01', planned: 20, actual: 17.8, optimistic: 17.8, pessimistic: 17.8 },
    { date: '2024-07-01', planned: 38, actual: 32.1, optimistic: 32.1, pessimistic: 32.1 },
    { date: '2024-09-01', planned: 54, actual: 47.0, optimistic: 47.0, pessimistic: 47.0 },
    { date: '2024-11-01', planned: 70, actual: null as unknown as number, optimistic: 62, pessimistic: 55 },
    { date: '2025-01-01', planned: 88, actual: null as unknown as number, optimistic: 75, pessimistic: 64 },
    { date: '2025-03-01', planned: 95, actual: null as unknown as number, optimistic: 85, pessimistic: 72 },
    { date: '2025-06-30', planned: 100, actual: null as unknown as number, optimistic: 95, pessimistic: 85 },
    { date: '2025-09-15', planned: null as unknown as number, actual: null as unknown as number, optimistic: 100, pessimistic: 97 },
    { date: '2025-12-31', planned: null as unknown as number, actual: null as unknown as number, optimistic: null as unknown as number, pessimistic: 100 },
  ],
  critical_path: [
    { id: 'a9', name: 'Welding Reach 3A-3B', discipline: 'Piping', risk_score: 0.91, delay_days: 12, reason: 'Current SPI=0.72, monsoon impact expected to worsen productivity.' },
    { id: 'a5', name: 'Valve Station VS-04 Foundation', discipline: 'Civil', risk_score: 0.84, delay_days: 8, reason: 'Concrete curing time + 3-day float consumed.' },
    { id: 'a4', name: 'Trench Excavation Reach 1-4', discipline: 'Civil', risk_score: 0.79, delay_days: 21, reason: 'Rock formation blasting permit pending; gates downstream piping.' },
    { id: 'a15', name: 'Substation Equipment Install', discipline: 'Electrical', risk_score: 0.68, delay_days: 6, reason: 'Equipment delivery delayed, 3-day float remaining.' },
    { id: 'a17', name: 'SCADA Panel Installation', discipline: 'Instrumentation', risk_score: 0.55, delay_days: 0, reason: 'FAT complete but transport & installation sequence tight.' },
  ],
}

// ─── Mock Anomalies ───────────────────────────────────────────────────────────
export const mockAnomalies: Anomaly[] = [
  {
    id: 'an1',
    type: 'productivity_drop',
    title: 'Productivity Drop — Piping Welding',
    description: 'Weld completion rate dropped 42% vs 30-day moving average. Current rate: 8 joints/day vs baseline 14 joints/day. Pattern consistent with wet/monsoon working conditions.',
    severity: 'critical',
    related_activity_id: 'a9',
    related_activity_name: 'Welding Reach 3A-3B',
    detected_at: new Date(Date.now() - 86400000).toISOString(),
    status: 'open',
  },
  {
    id: 'an2',
    type: 'schedule_deviation',
    title: 'Schedule Deviation — VS-04 Foundation',
    description: 'Activity started 14 days late. Current progress 45% vs planned 68% at this date. Float buffer fully consumed. Activity now on critical path.',
    severity: 'critical',
    related_activity_id: 'a5',
    related_activity_name: 'Valve Station VS-04 Foundation',
    detected_at: new Date(Date.now() - 172800000).toISOString(),
    status: 'investigating',
  },
  {
    id: 'an3',
    type: 'data_gap',
    title: 'Data Gap — Electrical Substation',
    description: 'No field progress reports received for activity ELE-SS-001 in last 7 days. Last reported progress: 8%. Investigate data submission from site supervisor.',
    severity: 'medium',
    related_activity_id: 'a15',
    related_activity_name: 'Substation Equipment Install',
    detected_at: new Date(Date.now() - 259200000).toISOString(),
    status: 'open',
  },
  {
    id: 'an4',
    type: 'weather_impact',
    title: 'Weather Risk — Monsoon Forecast',
    description: 'IMD forecast: heavy rainfall (>150mm/day) expected in project area for next 5 days. Historical data: similar events caused 3-7 day complete work stoppage in 2023.',
    severity: 'medium',
    detected_at: new Date(Date.now() - 43200000).toISOString(),
    status: 'open',
  },
]

// ─── Mock Memory / RAG Response ───────────────────────────────────────────────
export const mockMemoryAnswer: MemoryResponse = {
  answer: 'Based on institutional data from 12 similar EPC pipeline projects in NE India (2018–2024), the typical duration for 6-inch API 5L X-42 piping installation is **8–14 working days per km** under normal conditions. This includes pipe stringing, joint welding (cellulose electrodes, 3G/4G), NDT inspection, and coating. During monsoon season (June–Sep), productivity typically reduces by 35–45%, extending this to **12–22 days/km**. For your Kaziranga project, current performance suggests 15.3 days/km — within expected monsoon range.',
  confidence: 0.88,
  query_id: 'q-001',
  sources: [
    { id: 'src-1', project_name: 'Numaligarh Refinery Pipeline (2021)', activity_name: 'Pipeline Welding — 6-inch Section', date: '2021-08-14', excerpt: 'Reach 4 welding: 6.2 km completed in 87 working days = 14.0 days/km. Monsoon work stoppage: 12 days (Jul-Aug).', relevance: 0.94 },
    { id: 'src-2', project_name: 'Duliajan-Jorhat Gas Line (2022)', activity_name: 'Piping Installation — Phase 2', date: '2022-06-22', excerpt: '6-inch line, 8.4 km in 98 days including 3 weeks monsoon delay. Normalized: 8.6 days/km clear weather.', relevance: 0.89 },
    { id: 'src-3', project_name: 'Assam Trunk Pipeline (2019)', activity_name: 'Welding & Coating Works', date: '2019-10-05', excerpt: 'NDT pass rate 98.2%. Average joint welding rate: 22 joints/day (3 welding gangs). Joint length avg 12.2m.', relevance: 0.81 },
  ],
}
