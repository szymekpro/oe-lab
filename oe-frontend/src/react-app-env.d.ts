declare module '*.svg' {
  const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export { ReactComponent };
  export default src;
}

declare module '*.png';
declare module '*.jpg';
declare module '*.jpeg';
