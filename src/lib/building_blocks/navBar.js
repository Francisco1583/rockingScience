import logo from './assets/logo.png';
import launch from './assets/launch.png';
import analytics from './assets/analytics.png';

export default function Home() {
  return (
    <div className="navBar_div">
      <div className="logoDiv"><img className="logo" src={ logo }></img></div>
      <div className="optionDiv justifyOptions">
        <div className="container boton">
          <div className="justifyOptions">
            <img className="OptionImg" src={launch}></img>
          </div>
          <div>
            <h1>Launch</h1>
          </div>
        </div>
      </div>
      <div className="optionDiv justifyOptions">
        <div  className="container boton">
          <div className="justifyOptions">
            <img className="OptionImg" src={analytics}></img>
          </div>
          <div>
            <h1>Analytics</h1>
          </div>
        </div>
      </div>
      <div className="optionDiv">
        <div>3</div><div>31</div>
      </div>
    </div>
  );
}
