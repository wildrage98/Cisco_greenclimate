import 'dart:convert';
import 'dart:math';
import 'package:firebase_core/firebase_core.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_svg/flutter_svg.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => HomePageState();
}

class HomePageState extends State<HomePage> {
  final Set<Circle> _circles = <Circle>{};
  final Map<CircleId, Circle> _circleMap = <CircleId, Circle>{};
  var data;
  bool isLoading = true;

  List<LatLng> location = [
    const LatLng(37.520639, 126.888491),
    const LatLng(37.516330, 126.903525),
    const LatLng(37.533088, 126.888420), // 안양천 생태 공원
    const LatLng(37.527721, 126.916973), // 국회
    const LatLng(37.523319, 126.907100) // 아크로 타워 스퀘어
  ];
  List<String> info = [];
  var recommend = [];
  var recommendString = "";

  String areaName = "";

  @override
  void initState() {
    super.initState();
    //_loadData();
    _getData();
    _initializedCircles();
    recommendString = "";
  }

  void _getData() async {
    final url = Uri.https(
        'cisco-map-417104-default-rtdb.asia-southeast1.firebasedatabase.app',
        '.json');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        // Check for successful response
        final responseData = jsonDecode(response.body);
        setState(() {
          data = responseData;
          //print('success to load data: $data');
          isLoading = false; // Update loading state
        });
      } else {
        // Handle error or invalid response
        print('Failed to load data');
        setState(() {
          isLoading = false;
        });
      }
    } catch (e) {
      // Handle any exceptions
      print('Error: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  void _loadData() async {
    DatabaseReference ref = FirebaseDatabase.instance.ref("/");
    ref.onValue.listen((DatabaseEvent event) {
      final serverData = event.snapshot.value;
      if (serverData != null) {
        //print(serverData);
        setState(() {
          data = serverData;
        });
      } else {
        print("데이터 로딩 실패 또는 데이터가 존재하지 않음.");
      }
    }, onError: (error) {
      print("데이터 로딩 중 에러 발생: $error");
    });
  }

  void _initializedCircles() {
    for (int i = 0; i < location.length; i++) {
      Color c = Colors.primaries[Random().nextInt(Colors.primaries.length)];
      String id = "$i";
      Circle circle = Circle(
        circleId: CircleId(id),
        center: location[i],
        radius: 300, // meters
        strokeWidth: 2,
        strokeColor: c,
        fillColor: c.withOpacity(0.5),
        onTap: () {
          //print(data);
          var d = data['area$id'];
          _onCircleTapped(d['name'], d['climate'], d['recommend']);
        },
      );

      _circles.add(circle);
      _circleMap[circle.circleId] = circle;
    }

    setState(() {});
  }

  // 클릭된 원에 대한 처리
  void _onCircleTapped(
      String areaName, List<dynamic> info, List<dynamic> reco) {
    showDialog(
        context: context,
        builder: (context) => StatefulBuilder(// StatefulBuilder를 사용합니다.
                builder: (BuildContext context, StateSetter setState) {
              _getData();
              return AlertDialog(
                  title: Text(
                    areaName,
                    textAlign: TextAlign.center,
                  ),
                  content: FittedBox(
                      fit: BoxFit.fill,
                      child: Column(
                        children: [
                          Text("온도 : ${info[0].toStringAsFixed(2)} °C"),
                          Text("습도 : ${info[1].toStringAsFixed(2)} %"),
                          Text("CO2 농도 : ${info[2].toStringAsFixed(2)} ppm"),
                          Text("일조량 : ${info[3].toStringAsFixed(2)} 시간"),
                          Text("풍속 : ${info[4].toStringAsFixed(2)} m/s"),

                          const Divider(
                            height: 20,
                            thickness: 5,
                            indent: 20,
                            endIndent: 0,
                            color: Colors.black,
                          ),

                          //Text("평균 온도 : ${info[3].toStringAsFixed(2)} °C"),
                          //Text("평균 습도 : ${info[4].toStringAsFixed(2)} %"),
                          //Text("평균 CO2 농도 : ${info[5].toStringAsFixed(2)} ppm"),
                          //Text(
                          //"평균 일조량 : "), //${info[8].toStringAsFixed(2)} 시간"),
                          //Text(
                          //"평균 풍속 : "), //${info[9].toStringAsFixed(2)} m/s")
                        ],
                      )),
                  actions: <Widget>[
                    IconButton(
                      onPressed: () {
                        onPressGraph(areaName);
                      },
                      icon: const Icon(Icons.area_chart),
                    ),
                    TextButton(
                      child: const Text('확인'),
                      onPressed: () {
                        Navigator.of(context).pop();
                      },
                    )
                  ]);
            }));

    setState(() {
      recommendString =
          "1. ${reco[0]} : ${data['treeData'][reco[0]]}\n\n2. ${reco[1]} : ${data['treeData'][reco[1]]}\n\n3. ${reco[2]} : ${data['treeData'][reco[2]]}";
    });
  }

  void onPressGraph(areaName) {
    showDialog(
      context: context,
      builder: (BuildContext ctx) {
        return AlertDialog(
            title: Text(
              '$areaName 평균 기후',
              textAlign: TextAlign.center,
            ),
            content: FittedBox(
              fit: BoxFit.fill,
              child: Container(
                width: 500, // 차트의 너비 설정
                height: 200, // 차트의 높이 설정
                child: LineChart(
                  LineChartData(
                    gridData: FlGridData(show: false),
                    titlesData: FlTitlesData(
                      show: true,
                      rightTitles: AxisTitles(),
                      topTitles: AxisTitles(),
                      bottomTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          reservedSize: 30, // X축 타이틀의 높이
                          getTitlesWidget: (double value, TitleMeta meta) {
                            String text;
                            switch (value.toInt()) {
                              case 0:
                                text = 'Jan.';
                                break;
                              case 1:
                                text = 'Feb.';
                                break;
                              case 2:
                                text = 'Mar.';
                                break;
                              case 3:
                                text = 'Apr.';
                                break;
                              case 4:
                                text = 'May.';
                                break;
                              case 5:
                                text = 'Jun.';
                                break;
                              case 6:
                                text = 'Jul.';
                                break;
                              case 7:
                                text = 'Aug.';
                                break;
                              case 8:
                                text = 'Sep.';
                                break;
                              case 9:
                                text = 'Oct.';
                                break;
                              case 10:
                                text = 'Nov.';
                                break;
                              case 11:
                                text = 'Dec.';
                                break;
                              default:
                                text = '';
                            }
                            return Text(text,
                                style: TextStyle(
                                    color: Colors.black,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14));
                          },
                        ),
                      ),
                      leftTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          reservedSize: 40, // Y축 타이틀의 너비
                          getTitlesWidget: (double value, TitleMeta meta) {
                            // Y축 라벨 설정
                            return Text('${value.toInt()}°',
                                style: TextStyle(
                                    color: Colors.black,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14));
                          },
                        ),
                      ),
                    ),
                    borderData: FlBorderData(show: false),
                    lineBarsData: [
                      LineChartBarData(
                          spots: [
                            FlSpot(0, 1),
                            FlSpot(1, 4),
                            FlSpot(2, 10),
                            FlSpot(3, 18),
                            FlSpot(4, 23),
                            FlSpot(5, 27),
                            FlSpot(6, 29),
                            FlSpot(7, 29),
                            FlSpot(8, 25),
                            FlSpot(9, 20),
                            FlSpot(10, 11),
                            FlSpot(11, 4),
                          ],
                          isCurved: false,
                          color: Colors.blue,
                          barWidth: 4,
                          isStrokeCapRound: true,
                          dotData: FlDotData(show: true), // 데이터 점 표시
                          belowBarData: BarAreaData(show: false)),
                    ],
                  ),
                ),
              ),
            ),
            actions: <Widget>[
              TextButton(
                child: const Text('확인'),
                onPressed: () {
                  Navigator.of(context).pop();
                },
              ),
            ]);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    double width = MediaQuery.of(context).size.width;
    double height = MediaQuery.of(context).size.height;

    return Scaffold(
        appBar: AppBar(
          title:
              const Text('미기후에 따른 가로수 추천 시스템', style: TextStyle(fontSize: 30)),
          backgroundColor: Colors.green,
          foregroundColor: Colors.white,
          leading: IconButton(
            onPressed: () => {},
            icon: SvgPicture.asset(
              'assets/icons/cisco.svg',
              color: Colors.white,
            ),
            iconSize: 200,
          ),
        ),
        backgroundColor: Color(0xEFE7DA),
        body: SingleChildScrollView(
          child: Column(
            children: <Widget>[
              SizedBox(
                width: width * 0.9,
                height: height / 2,
                child: GoogleMap(
                  initialCameraPosition: const CameraPosition(
                    target: LatLng(37.525576, 126.899224), // 영등포구
                    zoom: 14.0,
                  ),
                  circles: _circles,
                ),
              ),
              SizedBox(width: width, height: height * 0.03),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const Column(children: [
                    Text(
                      "영등포구 평균 기후",
                      style:
                          TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      textAlign: TextAlign.center,
                    ),
                    Text(
                        "온도: 23 °C\n 습도: 70 %\n 광량: 360 루멘\n 풍속: 6 m/h\n CO2 농도: 3 ppm",
                        style: TextStyle(fontSize: 20),
                        textAlign: TextAlign.center),
                  ]),
                  SizedBox(width: width * 0.1),
                  SizedBox(
                      width: width * 0.6,
                      child: Column(
                        children: [
                          const Text("가로수 추천",
                              style: TextStyle(
                                  fontSize: 30, fontWeight: FontWeight.bold)),
                          Text(recommendString, style: TextStyle(fontSize: 20)),
                        ],
                      ))
                ],
              ),
            ],
          ),
        ));
  }
}
