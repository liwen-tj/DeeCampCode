import React, { Component } from 'react';
import ReactEcharts from 'echarts-for-react';
import echarts from 'echarts/lib/echarts';

class Pie extends Component {
    constructor(props) {
        super(props)
    }
    // while(!localStorage.getItem("statistic"))
    //     console.log("wait");
    render() {
        let dataStyle = {
            normal: {
                label: {
                    show: false
                },
                labelLine: {
                    show: false
                },
                shadowBlur: 0,
                shadowColor: '#203665'
            }
        };
        let ChartData = JSON.parse(this.props.chartData);
        let Chart1 = [0];
        let Chart2 = [0];
        if (ChartData.length != 0) {
            Chart1 = ChartData[0]["orRatio"];
            Chart2 = ChartData[0]["recoverRoomRatio"];
        }

        let option = {
            series: [
                {
                    name: '第二个圆环',
                    type: 'pie',
                    clockWise: false,
                    radius: [70, 80],
                    itemStyle: dataStyle,
                    hoverAnimation: false,
                    center: ['50%', '50%'],
                    data: [{
                        value: parseInt(Chart1 * 100),
                        label: {
                            normal: {
                                rich: {
                                    a: {
                                        color: '#d03e93',
                                        align: 'center',
                                        fontSize: 20,
                                        fontWeight: "bold"
                                    },
                                    b: {
                                        color: '#fff',
                                        align: 'center',
                                        fontSize: 16
                                    }
                                },
                                formatter: function (params) {
                                    return "\n{b|手术室整体利用率}\n\n" + "{a|" + params.value + "%}";
                                },
                                position: 'center',
                                show: true,
                                textStyle: {
                                    fontSize: '14',
                                    fontWeight: 'normal',
                                    color: '#fff'
                                }
                            }
                        },
                        itemStyle: {
                            normal: {
                                color: '#ef45ac',
                                shadowColor: '#ef45ac',
                                shadowBlur: 0
                            }
                        }
                    }, {
                        value: 100 - parseInt(Chart1 * 100),
                        name: 'invisible',
                        itemStyle: {
                            normal: {
                                color: '#412a4e'
                            },
                            emphasis: {
                                color: '#412a4e'
                            }
                        }
                    }]
                }, {
                    name: '第三个圆环',
                    type: 'pie',
                    clockWise: false,
                    radius: [70, 80],
                    itemStyle: dataStyle,
                    hoverAnimation: false,
                    center: ['85%', '50%'],
                    data: [{
                        value: parseInt(Chart2 * 100),
                        label: {
                            normal: {
                                rich: {
                                    a: {
                                        color: '#603dd0',
                                        align: 'center',
                                        fontSize: 20,
                                        fontWeight: "bold"
                                    },
                                    b: {
                                        color: '#fff',
                                        align: 'center',
                                        fontSize: 16
                                    }
                                },
                                formatter: function (params) {
                                    return "\n{b|手术室内复苏比率}\n\n" + "{a|" + params.value + "%}";
                                },
                                position: 'center',
                                show: true,
                                textStyle: {
                                    fontSize: '14',
                                    fontWeight: 'normal',
                                    color: '#fff'
                                }
                            }
                        },
                        itemStyle: {
                            normal: {
                                color: '#613fd1',
                                shadowColor: '#613fd1',
                                shadowBlur: 0
                            }
                        }
                    }, {
                        value: 100 - parseInt(Chart2 * 100),
                        name: 'invisible',
                        itemStyle: {
                            normal: {
                                color: '#453284'
                            },
                            emphasis: {
                                color: '#453284'
                            }
                        }
                    }]
                }]
        }
        return (
            <div>
                <ReactEcharts
                    option={option}
                    notMerge={true}
                    lazyUpdate={true}
                />
            </div>
        )
    };

}

class LineChart extends Component {
    // while (!localStorage.getItem("statistic"))
    //     console.log("wait");
    constructor(props) {
        super(props)
    }

    render() {
        console.log(JSON.parse(this.props.chartData)[0]);
        let data = [0];
        if (JSON.parse(this.props.chartData).length != 0)
            data = JSON.parse(this.props.chartData)[0]["extraHours"];
        // console.log(data);
        let dataAxis = [];
        let yMax = 1;
        let dataShadow = [];

        for (let i = 0; i < data.length; i++) {
            dataShadow.push(yMax);
            dataAxis.push(String(i + 1) + "号");
        }
        let option = {
            title: {
                text: '手术室加班时间(分钟)',
                textStyle: {
                    color: '#fff'
                }
            },
            grid: { // 控制图的大小，调整下面这些值就可以，
                x: 100,
                // x2: 40,
                y2: 80// y2可以控制 X轴跟Zoom控件之间的间隔，避免以为倾斜后造成 label重叠到zoom上
            },
            xAxis: {
                data: dataAxis,
                axisLabel: {
                    inside: false,
                    textStyle: {
                        color: '#fff'
                    },
                    interval: 0,
                    rotate: 30
                },
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: false
                },
                z: 10
            },
            yAxis: {
                splitLine: {
                    show: false
                },
                axisLine: {
                    show: false
                },
                axisTick: {
                    show: false
                },
                axisLabel: {
                    textStyle: {
                        color: '#fff'
                    }
                }
            },
            dataZoom: [
                {
                    type: 'inside'
                }
            ],
            series: [
                {
                    type: 'bar',
                    barWidth: 10,
                    barCategoryGap: 5,
                    itemStyle: {
                        normal: {
                            barBorderRadius: 5,
                            color: new echarts.graphic.LinearGradient(
                                0, 0, 0, 1,
                                [
                                    { offset: 0, color: '#a871ea' },
                                    { offset: 1, color: '#ea38bf' }
                                ]
                            )
                        },
                    },
                    data: data
                }
            ]
        }
        return (
            <div>
                <ReactEcharts
                    option={option}
                    notMerge={true}
                    lazyUpdate={true}
                />
            </div>
        )
    }
}

class LineChart2 extends Component {
    // while (!localStorage.getItem("statistic"))
    //     console.log("wait");
    constructor(props) {
        super(props)
    }

    render() {
        let data = [0];
        if (JSON.parse(this.props.chartData).length != 0)
            data = JSON.parse(this.props.chartData)[0]["everyorRatio"];
        // console.log(data);
        let dataAxis = [];
        let yMax = 1;
        let dataShadow = [];

        for (let i = 0; i < data.length; i++) {
            dataShadow.push(yMax);
            dataAxis.push(String(i + 1) + "号");
        }
        let option = {
            title: {
                text: '各手术室利用率',
                textStyle: {
                    color: '#fff'
                }
            },
            grid: { // 控制图的大小，调整下面这些值就可以，
                x: 100,
                // x2: 40,
                y2: 80// y2可以控制 X轴跟Zoom控件之间的间隔，避免以为倾斜后造成 label重叠到zoom上
            },
            xAxis: {
                data: dataAxis,
                axisLabel: {
                    inside: false,
                    textStyle: {
                        color: '#fff'
                    },
                    interval: 0,
                    rotate: 30
                },
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: false
                },
                z: 10
            },
            yAxis: {
                splitLine: {
                    show: false
                },
                axisLine: {
                    show: false
                },
                axisTick: {
                    show: false
                },
                axisLabel: {
                    textStyle: {
                        color: '#fff'
                    }
                }
            },
            dataZoom: [
                {
                    type: 'inside'
                }
            ],
            series: [
                {
                    type: 'bar',
                    barWidth: 10,
                    barCategoryGap: 5,
                    itemStyle: {
                        normal: {
                            barBorderRadius: 5,
                            color: new echarts.graphic.LinearGradient(
                                0, 0, 0, 1,
                                [
                                    { offset: 0, color: '#a871ea' },
                                    { offset: 1, color: '#ea38bf' }
                                ]
                            )
                        },
                    },
                    data: data
                }
            ]
        }
        return (
            <div>
                <ReactEcharts
                    option={option}
                    notMerge={true}
                    lazyUpdate={true}
                />
            </div>
        )
    }
}


class PredictChart extends Component {
    constructor(props) {
        super(props);
    }

    render() {

        let labelRight = {
            normal: {
                position: 'right'
            }
        }
        let labelLeft = {
            normal: {
                position: 'left'
            }
        }
        let data = [0];
        let key = this.props.jieshi_key;
        if (key >= 0)
            // console.log(this.props.jieshi_key);
            data = JSON.parse(localStorage.getItem("jieshi"))[key];
        console.log(data);
        data.sort(function (a, b) { return Math.abs(b[1]) - Math.abs(a[1]) });
        let list = new Array();
        for (let i = 0; i < 10; ++i) {
            list.push(data[i]);
        }

        let label = new Array();
        for (let i = 0; i < list.length; ++i) {
            if (list[i].length > 0 && list[i][0].indexOf("手术名称") != -1)
                label.push("手术名称");
            else if (list[i].length > 0 && list[i][0].indexOf("入院诊断") != -1)
                label.push("入院诊断");
            else
                label.push(list[i][0]);
        }

        let data2 = new Array();
        // console.log(list);
        let color = new Array();
        for (let i = 0; i < list.length; ++i) {
            let value = list[i][1];
            let temp = {};
            let good_color = new echarts.graphic.LinearGradient(
                0, 0, 0, 1,
                [
                    { offset: 0, color: '#a871ea' },
                    { offset: 1, color: '#ea38bf' }
                ]
            );

            let bad_color = new echarts.graphic.LinearGradient(
                0, 0, 0, 1,
                [
                    { offset: 0, color: '#4f41e1' },
                    { offset: 1, color: '#508eee' }
                ]
            );
            temp["value"] = value;
            temp["label"] = value > 0 ? labelLeft : labelRight;
            color[i] = value > 0 ? good_color : bad_color;
            data2.push(temp);
        }
        let x_max = 0;
        for (let i = 0; i < data2.length; ++i) {
            if (x_max < Math.abs(data2[i]["value"]))
                x_max = Math.abs(data2[i]["value"]);
        }
        x_max = Math.ceil(x_max);
        let option = {

            // title: {
            //     text: '交错正负轴标签'
            // },
            tooltip: {
                trigger: 'axis',
                axisPointer: { // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow' // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                top: 80,
                bottom: 30
            },
            xAxis: {
                type: 'value',
                position: 'top',
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                },
                axisLabel: {
                    interval: 0,
                    rotate: 30
                },
                min: x_max * -1,
                max: x_max

            },
            yAxis: {
                type: 'category',
                axisLine: {
                    show: false,
                },
                axisLabel: {
                    show: false,
                    interval: 30,
                },
                axisTick: {
                    show: false
                },
                splitLine: {
                    show: false
                },
                data: label,
            },
            series: [{
                name: '影响指数',
                type: 'bar',
                barWidth: 10,
                barCategoryGap: 5,
                itemStyle: {
                    normal: {
                        barBorderRadius: 5,
                        color: function (params) {
                            return color[params.dataIndex]
                        }
                    },
                },
                stack: '总量',
                label: {
                    normal: {
                        show: true,
                        formatter: '{b}'
                    }
                },
                data: data2
            }]
        }

        return (
            <div>
                <ReactEcharts
                    option={option}

                    notMerge={true}
                    lazyUpdate={true}
                />
            </div>
        )
    };

}

export { PredictChart, LineChart, Pie, LineChart2 };