import "./loader.css";

interface LoaderProps {
  children?: React.ReactNode;
  [key: string]: unknown;
}

const Loader = (props: LoaderProps) => {
  return (
    <div className="wrapper" {...props}>
      <div className="spinner"></div>
      <p>{props.children}</p>
    </div>
  );
};

export default Loader;