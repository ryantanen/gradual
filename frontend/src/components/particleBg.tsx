import { useEffect, useMemo, useState } from "react";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { Engine, ISourceOptions, type Container } from "@tsparticles/engine";
// import { loadAll } from "@tsparticles/all"; // if you are going to use `loadAll`, install the "@tsparticles/all" package too.
// import { loadFull } from "tsparticles"; // if you are going to use `loadFull`, install the "tsparticles" package too.
import { loadSlim } from "@tsparticles/slim"; // if you are going to use `loadSlim`, install the "@tsparticles/slim" package too.
// import { loadBasic } from "@tsparticles/basic"; // if you are going to use `loadBasic`, install the "@tsparticles/basic" package too.

export default function ParticleBg() {
  const [init, setInit] = useState(true);
  const particlesLoaded: (
    container?: Container | undefined
  ) => Promise<void> = async (container?: Container | undefined) => {
    console.log(container);
    // Perform asynchronous operations if needed
    // For example:
    // await someAsyncOperation();
  };
  const options: ISourceOptions = useMemo(
    () => ({
      background: {
        color: {
          value: "#f1f8ff",
        },
      },
      fpsLimit: 120,
      interactivity: {
        events: {
          onClick: {
            enable: true,
            mode: "push",
          },
          onHover: {
            enable: true,
            mode: "repulse",
          },
        },
        modes: {
          push: {
            quantity: 4,
          },
          repulse: {
            distance: 100,
            duration: 0.4,
          },
        },
      },
      particles: {
        color: {
          value: "#0069ff",
        },
        links: {
          color: "#0069ff",
          distance: 150,
          enable: true,
          opacity: 0.8,
          width: 1,
        },
        move: {
          direction: "none",
          enable: true,
          outModes: {
            default: "out",
          },
          random: false,
          speed: 1,
          straight: false,
        },
        number: {
          density: {
            enable: true,
          },
          value: 240,
        },
        opacity: {
          value: 0.5,
        },
        shape: {
          type: "circle",
        },
        size: {
          value: { min: 1, max: 5 },
        },
      },
      detectRetina: true,
    }),
    []
  );

  // this should be run only once per application lifetime
  useEffect(() => {
    initParticlesEngine(async (engine: Engine) => {
      // you can initiate the tsParticles instance (engine) here, adding custom shapes or presets
      // this loads the tsparticles package bundle, it's the easiest method for getting everything ready
      // starting from v2 you can add only the features you need reducing the bundle size
      //await loadAll(engine);
      //await loadFull(engine);
      await loadSlim(engine);
      //await loadBasic(engine);
    }).then(() => {
      setInit(true);
    });
  }, []);

  if (init) {
    return (
      <Particles
        id="tsparticles"
        options={options}
        particlesLoaded={particlesLoaded}
      />
    );
  }

  return "";
}
