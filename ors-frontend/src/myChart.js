import React, { Component } from 'react';
import ReactEcharts from 'echarts-for-react';
import echarts from 'echarts/lib/echarts';
import { transformDirection } from 'echarts/lib/util/graphic';

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}
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
        console.log(this.props.chartData);
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
                text: '手术室加班时间',
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
        console.log(this.props.chartData);
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

    componentDidMount() { }

    getOption() {
        let labelRight = {
            normal: {
                position: 'right'
            }
        };

        let labelLeft = {
            normal: {
                position: 'left'
            }
        }
        return {
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
                }
            },
            yAxis: {
                type: 'category',
                axisLine: {
                    show: false
                },
                axisLabel: {
                    show: false,
                },
                axisTick: {
                    show: false
                },
                splitLine: {
                    show: false
                },
                data: ['six', 'five', 'four', 'three', 'two', 'one']
            },
            series: [{
                name: '生活费',
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
                stack: '总量',
                label: {
                    normal: {
                        show: true,
                        formatter: '{b}'
                    }
                },
                data: [{
                    value: -0.07,
                    label: labelRight
                },
                {
                    value: -0.09,
                    label: labelRight
                },
                {
                    value: 0.2,
                    label: labelLeft
                },

                {
                    value: 0.44,
                    label: labelLeft
                },
                {
                    value: -0.23,
                    label: labelRight
                },
                {
                    value: 0.8,
                    label: labelLeft
                },
                ]
            }]
        }

    };

    render() {
        return (
            <div>
                <ReactEcharts
                    option={this.getOption()}
                    notMerge={true}
                    lazyUpdate={true}
                />
            </div>
        )
    }
}

export { PredictChart, LineChart, Pie, LineChart2 };