import React from 'react';
import { Button, Drawer, Icon, message, Upload } from 'antd';
import background from './img/back1.jpg';
import './App.css';
import 'antd/dist/antd.css';
import MyForm from './MyForm';
class App extends React.Component {

  state = { visible: false };

  showDrawer = () => {
    this.setState({
      visible: true,
    });
  };

  onClose = () => {
    this.setState({
      visible: false,
    });
  };

  handleSubmit = e => {
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        console.log('Received values of form: ', values);
      }
    });
  };

  render() {
    const props = {
      name: 'file',
      action: 'http://127.0.0.1:5000/fake_upload',
      headers: {
        authorization: 'authorization-text',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
      },
      accept: ".csv",
      onChange(info) {
        if (info.file.status !== 'uploading') {
          console.log(info.file, info.fileList);
        }
        if (info.file.status === 'done') {
          message.success(`${info.file.name} 首页文件上传成功`);
        } else if (info.file.status === 'error') {
          message.error(`${info.file.name} 首页文件上传失败`);
        }
      },
    };
    return (
      <div className="App" style={{ backgroundImage: `url(${background})` }}>
        <div className="page">
          <div className="head">
            <Upload {...props}>
              <Button style={{ marginTop: "250%", marginLeft:"110%" }} type="primary" size="large">
                <Icon type="upload" /> 上传历史患者信息表
              </Button>
            </Upload>
            <Button style={{ marginTop: "32.5%", marginLeft: "25%" }} type="primary" size="large" onClick={this.showDrawer}>
              构建调度表
              </Button>
          </div>
          <Drawer
            title="配置信息"
            placement="right"
            closable={true}
            onClose={this.onClose}
            visible={this.state.visible}
          >
            <MyForm />
          </Drawer>
        </div>
      </div>
    );
  }
}

export default App;
