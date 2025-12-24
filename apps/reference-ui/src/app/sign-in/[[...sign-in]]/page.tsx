import { SignIn } from '@clerk/nextjs'

export function generateStaticParams() {
  return [{ 'sign-in': [] }]
}

export default function SignInPage() {
  return (
    <div className="flex justify-center items-center h-screen">
      <SignIn />
    </div>
  )
}
