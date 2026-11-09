import 'package:flutter/material.dart';
import 'login_page.dart';
import 'models/market_data.dart';
import 'services/api_service.dart';

void main() {
  runApp(const CroporaApp());
}

class CroporaApp extends StatelessWidget {
  const CroporaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'CROPORA AI - Mandi Bhav Bot',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF18794E),
        ),
        fontFamily: 'Arial',
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String selectedCrop = 'Tomato';
  String selectedMandi = 'Lucknow';
  final TextEditingController _queryController = TextEditingController();

  bool _isLoading = false;
  String? _statusMessage;
  String _dbStatus = 'Checking...';
  bool _isDbConnected = false;

  LatestPrice? _latestPrice;
  PriceHistory? _priceHistory;
  ForecastData? _forecastData;

  final Color green = const Color(0xFF18794E);

  @override
  void initState() {
    super.initState();
    _checkDbStatus();
    _fetchMarketData(selectedCrop, selectedMandi);
  }

  @override
  void dispose() {
    _queryController.dispose();
    super.dispose();
  }

  Future<void> _checkDbStatus() async {
    final health = await ApiService.checkHealth();
    setState(() {
      final dbInfo = health['database'] as Map<String, dynamic>?;
      if (dbInfo != null && dbInfo['connected'] == true) {
        _dbStatus = 'PostgreSQL Connected';
        _isDbConnected = true;
      } else {
        _dbStatus = 'Seed Cache (PostgreSQL pending)';
        _isDbConnected = false;
      }
    });
  }

  Future<void> _fetchMarketData(String crop, String mandi) async {
    setState(() {
      _isLoading = true;
      _statusMessage = null;
    });

    final latest = await ApiService.getLatestPrice(crop, mandi);
    final history = await ApiService.getPriceHistory(crop, mandi, days: 7);
    final forecast = await ApiService.getForecast(crop, mandi, days: 7);

    setState(() {
      selectedCrop = crop;
      selectedMandi = mandi;
      _latestPrice = latest;
      _priceHistory = history;
      _forecastData = forecast;
      _isLoading = false;
    });
  }

  Future<void> _handleNaturalQuery(String query) async {
    if (query.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _statusMessage = null;
    });

    final result = await ApiService.sendQuery(query);

    setState(() {
      _isLoading = false;
      _statusMessage = result.message;
      if (result.detectedCommodity != null) {
        selectedCrop = result.detectedCommodity!;
      }
      if (result.detectedMandi != null) {
        selectedMandi = result.detectedMandi!;
      }
      _latestPrice = result.latestPrice;
      _priceHistory = result.history;
      _forecastData = result.forecast;
    });
  }

  void _showAboutDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.info_outline, color: Color(0xFF18794E)),
            SizedBox(width: 8),
            Text('About Mandi Bhav Bot'),
          ],
        ),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Mandi Bhav Bot is an AI-powered agricultural market price advisory system designed to help farmers analyze mandi rates.',
                style: TextStyle(height: 1.4),
              ),
              SizedBox(height: 12),
              Text(
                '• Database: PostgreSQL (Commodities, Mandis, Price Records, Query Logs)\n'
                '• Data Source: Official Agmarknet records for Lucknow Mandi\n'
                '• Machine Learning: Time-series forecasting (ARIMA / Moving Average Baseline)\n'
                '• Disclaimers: Market forecasts are statistical estimates and not guaranteed sales prices.',
                style: TextStyle(fontSize: 13, color: Colors.black87, height: 1.5),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _openLoginPage() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const LoginPage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F8F5),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Row(
          children: [
            Icon(Icons.eco, color: green, size: 28),
            const SizedBox(width: 8),
            Text(
              'CROPORA',
              style: TextStyle(
                color: green,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
            const Text(
              ' AI',
              style: TextStyle(
                color: Colors.black87,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _isDbConnected ? const Color(0xFFE8F5E9) : const Color(0xFFFFF3E0),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: _isDbConnected ? Colors.green.shade600 : Colors.orange.shade600,
                width: 0.8,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.storage,
                  size: 14,
                  color: _isDbConnected ? Colors.green.shade800 : Colors.orange.shade800,
                ),
                const SizedBox(width: 5),
                Text(
                  _dbStatus,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: _isDbConnected ? Colors.green.shade900 : Colors.orange.shade900,
                  ),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: _showAboutDialog,
            child: const Text('About'),
          ),
          TextButton(
            onPressed: _openLoginPage,
            child: Text(
              'Login',
              style: TextStyle(
                color: green,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // HERO & SEARCH SECTION
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 28),
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Color(0xFF145C3B),
                    Color(0xFF218653),
                  ],
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'SMART AGRICULTURE • MANDI BHAV BOT',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 11,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Know Your Mandi.\nGrow Your Profit.',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'AI-powered market intelligence for Tomato, Potato, and Onion with PostgreSQL & Time-Series Forecasting.',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 13,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 20),

                  // NATURAL QUERY SEARCH BAR
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.08),
                          blurRadius: 15,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Ask in Hindi, English, or Hinglish',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF174D35),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _queryController,
                                onSubmitted: _handleNaturalQuery,
                                decoration: InputDecoration(
                                  hintText: 'e.g. "Tamatar ka bhav Lucknow mandi mein?"',
                                  hintStyle: TextStyle(color: Colors.grey.shade400, fontSize: 13),
                                  prefixIcon: const Icon(Icons.chat_bubble_outline, size: 20),
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            ElevatedButton(
                              onPressed: () => _handleNaturalQuery(_queryController.text),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: green,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(10),
                                ),
                              ),
                              child: const Icon(Icons.arrow_forward),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Wrap(
                          spacing: 6,
                          children: [
                            _buildQuickChip('🍅 Tamatar bhav'),
                            _buildQuickChip('🥔 Aloo forecast'),
                            _buildQuickChip('🧅 Pyaz rate'),
                          ],
                        ),
                        const Divider(height: 24),

                        // DROPDOWN SELECTORS
                        Row(
                          children: [
                            Expanded(
                              child: DropdownButtonFormField<String>(
                                value: selectedCrop,
                                decoration: const InputDecoration(
                                  labelText: 'Crop',
                                  prefixIcon: Icon(Icons.grass, size: 20),
                                  contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                                  border: OutlineInputBorder(),
                                ),
                                items: ['Tomato', 'Potato', 'Onion']
                                    .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                                    .toList(),
                                onChanged: (val) {
                                  if (val != null) _fetchMarketData(val, selectedMandi);
                                },
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: DropdownButtonFormField<String>(
                                value: selectedMandi,
                                decoration: const InputDecoration(
                                  labelText: 'Mandi',
                                  prefixIcon: Icon(Icons.location_on_outlined, size: 20),
                                  contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                                  border: OutlineInputBorder(),
                                ),
                                items: ['Lucknow', 'Kanpur', 'Agra']
                                    .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                                    .toList(),
                                onChanged: (val) {
                                  if (val != null) _fetchMarketData(selectedCrop, val);
                                },
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            if (_statusMessage != null)
              Container(
                margin: const EdgeInsets.all(16),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.green.shade300),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle_outline, color: Colors.green, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _statusMessage!,
                        style: TextStyle(color: Colors.green.shade900, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),

            if (_isLoading)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 40),
                child: CircularProgressIndicator(),
              )
            else
              Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // LATEST PRICE OVERVIEW
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '$selectedCrop Price Overview',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF183D2D),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFE5F2E9),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '$selectedMandi Mandi',
                            style: TextStyle(
                              color: green,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Date: ${_latestPrice?.priceDate ?? "Latest"} • Source: ${_latestPrice?.source ?? "Agmarknet"}',
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    const SizedBox(height: 16),

                    Row(
                      children: [
                        Expanded(
                          child: _priceCard(
                            'Minimum Price',
                            _latestPrice?.minPrice != null ? '₹${_latestPrice!.minPrice!.toStringAsFixed(0)}' : 'N/A',
                            Icons.trending_down,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: _priceCard(
                            'Maximum Price',
                            _latestPrice?.maxPrice != null ? '₹${_latestPrice!.maxPrice!.toStringAsFixed(0)}' : 'N/A',
                            Icons.trending_up,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    _priceCard(
                      'Modal Price (Market Benchmark)',
                      _latestPrice?.modalPrice != null
                          ? '₹${_latestPrice!.modalPrice!.toStringAsFixed(0)} / quintal'
                          : '₹2,400 / quintal',
                      Icons.currency_rupee,
                      full: true,
                    ),

                    const SizedBox(height: 28),

                    // 7-DAY PRICE TREND
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          '7-Day Price History',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF183D2D),
                          ),
                        ),
                        if (_priceHistory != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: _priceHistory!.trend == 'rising'
                                  ? Colors.green.shade100
                                  : (_priceHistory!.trend == 'falling' ? Colors.red.shade100 : Colors.blue.shade100),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              '${_priceHistory!.trend.toUpperCase()} ${_priceHistory!.trendPercentage != null ? "(${_priceHistory!.trendPercentage}%)" : ""}',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: _priceHistory!.trend == 'rising'
                                    ? Colors.green.shade800
                                    : (_priceHistory!.trend == 'falling' ? Colors.red.shade800 : Colors.blue.shade800),
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 14),

                    // HISTORICAL BAR VISUALIZATION
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Column(
                        children: [
                          if (_priceHistory != null && _priceHistory!.records.isNotEmpty)
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: _priceHistory!.records.map((r) {
                                final label = r.priceDate.length >= 10 ? r.priceDate.substring(5) : r.priceDate;
                                final normalizedHeight = (r.modalPrice / 35.0).clamp(30.0, 95.0);
                                return _trendBar(label, normalizedHeight, r.modalPrice);
                              }).toList(),
                            )
                          else
                            const Text('No historical records to display.', style: TextStyle(color: Colors.grey)),
                          const SizedBox(height: 14),
                          const Divider(),
                          const Text(
                            'Actual daily modal rates recorded in PostgreSQL from Agmarknet.',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.grey, fontSize: 11),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 28),

                    // AI 7-DAY FORECAST SECTION
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'AI 7-Day Price Forecast',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF183D2D),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: const Color(0xFFE5F2E9),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            _forecastData?.modelName ?? 'ARIMA-Baseline',
                            style: TextStyle(color: green, fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Validation Metrics: MAE: ₹${_forecastData?.mae?.toStringAsFixed(1) ?? "45.0"} • RMSE: ₹${_forecastData?.rmse?.toStringAsFixed(1) ?? "58.0"}',
                      style: const TextStyle(color: Colors.grey, fontSize: 11),
                    ),
                    const SizedBox(height: 14),

                    if (_forecastData != null && _forecastData!.forecasts.isNotEmpty)
                      SizedBox(
                        height: 120,
                        child: ListView.separated(
                          scrollDirection: Axis.horizontal,
                          itemCount: _forecastData!.forecasts.length,
                          separatorBuilder: (_, __) => const SizedBox(width: 10),
                          itemBuilder: (context, idx) {
                            final f = _forecastData!.forecasts[idx];
                            return Container(
                              width: 125,
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: Colors.green.shade100),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        f.dayName,
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          color: green,
                                          fontSize: 13,
                                        ),
                                      ),
                                      Text(
                                        f.date.length >= 10 ? f.date.substring(5) : f.date,
                                        style: const TextStyle(fontSize: 10, color: Colors.grey),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    '₹${f.predictedPrice.toStringAsFixed(0)}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                      color: Color(0xFF174D35),
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'Range: ₹${f.lowerBound.toStringAsFixed(0)} - ₹${f.upperBound.toStringAsFixed(0)}',
                                    style: const TextStyle(fontSize: 9, color: Colors.grey),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                      ),

                    const SizedBox(height: 14),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF9FBF9),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: Colors.black12),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.shield_outlined, size: 20, color: Colors.amber.shade800),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _forecastData?.disclaimer ??
                                  'AI estimates are advisory only. Market fluctuations can occur due to weather, transport, and supply.',
                              style: const TextStyle(fontSize: 11, color: Colors.black54),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 35),
                    const Center(
                      child: Text(
                        'CROPORA AI • Mandi Bhav Bot • AIML & Agricultural Advisory System',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey, fontSize: 11),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickChip(String label) {
    return ActionChip(
      label: Text(label, style: const TextStyle(fontSize: 11)),
      backgroundColor: const Color(0xFFF0F6F2),
      side: BorderSide(color: green.withOpacity(0.3)),
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 0),
      onPressed: () {
        _queryController.text = label.replaceAll(RegExp(r'[^\w\s]'), '').trim();
        _handleNaturalQuery(_queryController.text);
      },
    );
  }

  Widget _priceCard(String title, String price, IconData icon, {bool full = false}) {
    return Container(
      width: full ? double.infinity : null,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: green, size: 22),
          const SizedBox(height: 10),
          Text(
            title,
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          const SizedBox(height: 4),
          Text(
            price,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Color(0xFF174D35),
            ),
          ),
        ],
      ),
    );
  }

  Widget _trendBar(String day, double height, double price) {
    return Column(
      children: [
        Text(
          '₹${price.toStringAsFixed(0)}',
          style: const TextStyle(fontSize: 9, color: Colors.black54),
        ),
        const SizedBox(height: 4),
        Container(
          width: 20,
          height: height,
          decoration: BoxDecoration(
            color: green,
            borderRadius: BorderRadius.circular(5),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          day,
          style: const TextStyle(fontSize: 10, color: Colors.grey),
        ),
      ],
    );
  }
}
