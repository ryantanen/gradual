import { useState } from "react";

import { Button } from "./components/ui/button";

function App() {
  return (
    <div>
      <div className="flex flex-col items-center justify-center h-screen">
        <h1 className="text-4xl font-bold">Gradual Me</h1>
        <Button>Get Started</Button>
        <Button variant="outline">Login</Button>
      </div>
    </div>
  );
}

export default App;
