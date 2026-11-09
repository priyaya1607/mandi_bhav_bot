class LatestPrice {
  final String commodity;
  final String mandi;
  final bool dataAvailable;
  final String? priceDate;
  final double? minPrice;
  final double? maxPrice;
  final double? modalPrice;
  final String unit;
  final String? source;
  final String? message;

  LatestPrice({
    required this.commodity,
    required this.mandi,
    required this.dataAvailable,
    this.priceDate,
    this.minPrice,
    this.maxPrice,
    this.modalPrice,
    this.unit = "₹/Quintal",
    this.source = "Agmarknet",
    this.message,
  });

  factory LatestPrice.fromJson(Map<String, dynamic> json) {
    return LatestPrice(
      commodity: json['commodity'] ?? '',
      mandi: json['mandi'] ?? '',
      dataAvailable: json['data_available'] ?? false,
      priceDate: json['price_date'],
      minPrice: (json['min_price'] as num?)?.toDouble(),
      maxPrice: (json['max_price'] as num?)?.toDouble(),
      modalPrice: (json['modal_price'] as num?)?.toDouble(),
      unit: json['unit'] ?? '₹/Quintal',
      source: json['source'] ?? 'Agmarknet',
      message: json['message'],
    );
  }
}

class PriceRecord {
  final String priceDate;
  final double? minPrice;
  final double? maxPrice;
  final double modalPrice;
  final String unit;
  final String source;

  PriceRecord({
    required this.priceDate,
    this.minPrice,
    this.maxPrice,
    required this.modalPrice,
    this.unit = "₹/Quintal",
    this.source = "Agmarknet",
  });

  factory PriceRecord.fromJson(Map<String, dynamic> json) {
    return PriceRecord(
      priceDate: json['price_date'] ?? '',
      minPrice: (json['min_price'] as num?)?.toDouble(),
      maxPrice: (json['max_price'] as num?)?.toDouble(),
      modalPrice: (json['modal_price'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] ?? '₹/Quintal',
      source: json['source'] ?? 'Agmarknet',
    );
  }
}

class PriceHistory {
  final String commodity;
  final String mandi;
  final bool dataAvailable;
  final int recordCount;
  final String trend; // "rising", "falling", "stable"
  final double? trendPercentage;
  final List<PriceRecord> records;
  final String? message;

  PriceHistory({
    required this.commodity,
    required this.mandi,
    required this.dataAvailable,
    required this.recordCount,
    required this.trend,
    this.trendPercentage,
    required this.records,
    this.message,
  });

  factory PriceHistory.fromJson(Map<String, dynamic> json) {
    final list = json['records'] as List<dynamic>? ?? [];
    return PriceHistory(
      commodity: json['commodity'] ?? '',
      mandi: json['mandi'] ?? '',
      dataAvailable: json['data_available'] ?? false,
      recordCount: json['record_count'] ?? 0,
      trend: json['trend'] ?? 'stable',
      trendPercentage: (json['trend_percentage'] as num?)?.toDouble(),
      records: list.map((item) => PriceRecord.fromJson(item)).toList(),
      message: json['message'],
    );
  }
}

class ForecastItem {
  final String date;
  final String dayName;
  final double predictedPrice;
  final double lowerBound;
  final double upperBound;

  ForecastItem({
    required this.date,
    required this.dayName,
    required this.predictedPrice,
    required this.lowerBound,
    required this.upperBound,
  });

  factory ForecastItem.fromJson(Map<String, dynamic> json) {
    return ForecastItem(
      date: json['date'] ?? '',
      dayName: json['day_name'] ?? '',
      predictedPrice: (json['predicted_price'] as num?)?.toDouble() ?? 0.0,
      lowerBound: (json['lower_bound'] as num?)?.toDouble() ?? 0.0,
      upperBound: (json['upper_bound'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class ForecastData {
  final String commodity;
  final String mandi;
  final bool dataAvailable;
  final String modelName;
  final int horizonDays;
  final String trendDirection;
  final List<ForecastItem> forecasts;
  final double? mae;
  final double? rmse;
  final String disclaimer;
  final String? message;

  ForecastData({
    required this.commodity,
    required this.mandi,
    required this.dataAvailable,
    required this.modelName,
    this.horizonDays = 7,
    this.trendDirection = "stable",
    required this.forecasts,
    this.mae,
    this.rmse,
    required this.disclaimer,
    this.message,
  });

  factory ForecastData.fromJson(Map<String, dynamic> json) {
    final list = json['forecasts'] as List<dynamic>? ?? [];
    return ForecastData(
      commodity: json['commodity'] ?? '',
      mandi: json['mandi'] ?? '',
      dataAvailable: json['data_available'] ?? false,
      modelName: json['model_name'] ?? '',
      horizonDays: json['horizon_days'] ?? 7,
      trendDirection: json['trend_direction'] ?? 'stable',
      forecasts: list.map((item) => ForecastItem.fromJson(item)).toList(),
      mae: (json['mae'] as num?)?.toDouble(),
      rmse: (json['rmse'] as num?)?.toDouble(),
      disclaimer: json['disclaimer'] ?? '',
      message: json['message'],
    );
  }
}

class NaturalQueryResult {
  final String query;
  final String? detectedCommodity;
  final String? detectedMandi;
  final String detectedIntent;
  final bool success;
  final String message;
  final LatestPrice? latestPrice;
  final PriceHistory? history;
  final ForecastData? forecast;

  NaturalQueryResult({
    required this.query,
    this.detectedCommodity,
    this.detectedMandi,
    required this.detectedIntent,
    required this.success,
    required this.message,
    this.latestPrice,
    this.history,
    this.forecast,
  });

  factory NaturalQueryResult.fromJson(Map<String, dynamic> json) {
    return NaturalQueryResult(
      query: json['query'] ?? '',
      detectedCommodity: json['detected_commodity'],
      detectedMandi: json['detected_mandi'],
      detectedIntent: json['detected_intent'] ?? 'latest_price',
      success: json['success'] ?? false,
      message: json['message'] ?? '',
      latestPrice: json['latest_price'] != null
          ? LatestPrice.fromJson(json['latest_price'])
          : null,
      history: json['history'] != null
          ? PriceHistory.fromJson(json['history'])
          : null,
      forecast: json['forecast'] != null
          ? ForecastData.fromJson(json['forecast'])
          : null,
    );
  }
}
